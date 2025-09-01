from sqlalchemy import text
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Tuple
import math, time

class SearchRepository:
    def __init__(self, session: Session):
        self.session = session

    # --- Low level primitives -------------------------------------------------
    def vector_search(self, embedding: list[float], top_k: int) -> List[Dict[str, Any]]:
        sql = text(
            """
            SELECT c.id, c.text, c.page, c.section, d.title,
                   (e.embedding <-> (:embedding)::vector) AS distance
            FROM embeddings e
            JOIN chunks c ON c.id = e.chunk_id
            JOIN documents d ON d.id = c.document_id
            ORDER BY e.embedding <-> (:embedding)::vector
            LIMIT :limit
            """
        )
        res = self.session.execute(sql, {"embedding": embedding, "limit": top_k})
        rows = res.mappings().all()
        out: List[Dict[str, Any]] = []
        for r in rows:
            dist = r["distance"]
            # Convert L2 distance (for pgvector default) into a bounded similarity proxy.
            score = 1 / (1 + float(dist))
            out.append({
                "id": str(r["id"]),
                "text": r["text"],
                "page": r["page"],
                "section": r["section"],
                "title": r["title"],
                "score": score,
                "distance": float(dist),
                "source": "vector"
            })
        return out

    def lexical_search(self, query: str, top_k: int) -> List[Dict[str, Any]]:
        sql = text(
            """
            SELECT c.id, c.text, c.page, c.section, d.title,
                   ts_rank_cd(to_tsvector('english', c.text), plainto_tsquery('english', :q)) AS rank
            FROM chunks c
            JOIN documents d ON d.id = c.document_id
            WHERE to_tsvector('english', c.text) @@ plainto_tsquery('english', :q)
            ORDER BY rank DESC
            LIMIT :limit
            """
        )
        res = self.session.execute(sql, {"q": query, "limit": top_k})
        rows = res.mappings().all()
        out: List[Dict[str, Any]] = []
        for r in rows:
            out.append({
                "id": str(r["id"]),
                "text": r["text"],
                "page": r["page"],
                "section": r["section"],
                "title": r["title"],
                "score": float(r["rank"]) if r["rank"] else 0.0,
                "distance": None,
                "source": "lexical"
            })
        return out

    def rrf(self, lists: List[List[Dict[str, Any]]], k: int) -> List[Dict[str, Any]]:
        if not lists:
            return []
        scores: Dict[str, Dict[str, Any]] = {}
        for l in lists:
            for rank, item in enumerate(l, start=1):
                entry = scores.setdefault(item['id'], {**item, 'rrf': 0.0})
                entry['rrf'] += 1 / (k + rank)
        merged = list(scores.values())
        merged.sort(key=lambda x: x['rrf'], reverse=True)
        return merged

    def mmr(self, candidates: List[Dict[str, Any]], lambda_mult: float, top_m: int) -> List[Dict[str, Any]]:
        if len(candidates) <= top_m:
            return candidates
        selected: List[Dict[str, Any]] = []
        remaining = candidates.copy()
        while remaining and len(selected) < top_m:
            if not selected:
                selected.append(remaining.pop(0))
                continue
            best_idx = 0
            best_score = -1e9
            for i, cand in enumerate(remaining):
                relevance = cand['score']
                diversity = max(similarity(cand, s) for s in selected)
                mmr_score = lambda_mult * relevance - (1 - lambda_mult) * diversity
                if mmr_score > best_score:
                    best_score = mmr_score
                    best_idx = i
            selected.append(remaining.pop(best_idx))
        return selected

    # --- Orchestration --------------------------------------------------------
    def hybrid_retrieve(
        self,
        query: str,
        query_embedding: list[float],
        top_k: int,
        use_lexical: bool,
        rrf_k: int,
        mmr_lambda: float,
        final_k: int,
        threshold: float,
    ) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """Run vector (and optionally lexical) retrieval, fuse, filter, then MMR + trim.

        Returns: (final_context_chunks, stats)
        stats keys: {'vector', 'lexical', 'fused', 'after_threshold', 'final', 'timings'}
        """
        t_start = time.perf_counter()
        t_vec0 = time.perf_counter()
        vec = self.vector_search(query_embedding, top_k)
        t_vec1 = time.perf_counter()
        lists: List[List[Dict[str, Any]]] = [vec]
        lex: List[Dict[str, Any]] = []
        if use_lexical:
            t_lex0 = time.perf_counter()
            lex = self.lexical_search(query, top_k)
            t_lex1 = time.perf_counter()
            lists.append(lex)
        else:
            t_lex0 = t_lex1 = None  # type: ignore
        if len(lists) > 1:
            fused = self.rrf(lists, rrf_k)
        else:
            fused = vec
        # Dedup identical text early
        seen_text = set()
        deduped: List[Dict[str, Any]] = []
        for item in fused:
            key = item['text'][:500]
            if key in seen_text:
                continue
            seen_text.add(key)
            deduped.append(item)
        # Apply similarity threshold (vector-derived score only); keep lexical-only items if hybrid but mark them low
        filtered: List[Dict[str, Any]] = []
        for item in deduped:
            if item['source'] == 'vector' and item['score'] >= threshold:
                filtered.append(item)
            elif item['source'] == 'lexical' and use_lexical:
                filtered.append(item)
        if not filtered:
            # fallback: use top items ignoring threshold
            filtered = deduped[:final_k]
        # MMR to reduce redundancy
        mmr_applied = self.mmr(filtered, mmr_lambda, final_k)
        t_end = time.perf_counter()
        stats = {
            'vector': len(vec),
            'lexical': len(lex),
            'fused': len(fused),
            'after_threshold': len(filtered),
            'final': len(mmr_applied),
            'timings': {
                'vector_ms': int((t_vec1 - t_vec0) * 1000),
                'lexical_ms': int(((t_lex1 - t_lex0) * 1000) if use_lexical and t_lex0 and t_lex1 else 0),
                'total_retrieve_ms': int((t_end - t_start) * 1000),
            }
        }
        return mmr_applied, stats

def similarity(a: Dict[str, Any], b: Dict[str, Any]) -> float:
    # crude textual overlap similarity
    set_a = set(a['text'][:500].split())
    set_b = set(b['text'][:500].split())
    if not set_a or not set_b:
        return 0.0
    return len(set_a & set_b) / len(set_a | set_b)
