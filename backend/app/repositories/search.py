from sqlalchemy import text
from sqlalchemy.orm import Session
from typing import List, Dict, Any

class SearchRepository:
    def __init__(self, session: Session):
        self.session = session

    def vector_search(self, embedding: list[float], top_k: int) -> List[Dict[str, Any]]:
        # pgvector requires vector <-> vector; passing a bare array param becomes numeric[] and fails.
        # Build an inline vector literal safely (embedding values are floats from model).
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
            score = 1 / (1 + dist)
            out.append(
                {
                    "id": str(r["id"]),
                    "text": r["text"],
                    "page": r["page"],
                    "section": r["section"],
                    "title": r["title"],
                    "score": score,
                }
            )
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
            out.append(
                {
                    "id": str(r["id"]),
                    "text": r["text"],
                    "page": r["page"],
                    "section": r["section"],
                    "title": r["title"],
                    "score": float(r["rank"]) if r["rank"] else 0.0,
                }
            )
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

def similarity(a: Dict[str, Any], b: Dict[str, Any]) -> float:
    # crude textual overlap similarity
    set_a = set(a['text'][:500].split())
    set_b = set(b['text'][:500].split())
    if not set_a or not set_b:
        return 0.0
    return len(set_a & set_b) / len(set_a | set_b)
