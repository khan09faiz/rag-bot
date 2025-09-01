from typing import List, Dict, Any
from sqlalchemy.orm import Session
from app.repositories.search import SearchRepository
from app.core.config import settings
from .embedding_service import embed_query

def retrieve(query: str, db: Session, top_k: int, hybrid: bool) -> List[Dict[str, Any]]:
    repo = SearchRepository(db)
    q_vec = embed_query(query)
    vec_results = repo.vector_search(q_vec, top_k)
    lists = [vec_results]
    if hybrid:
        lex = repo.lexical_search(query, top_k)
        lists.append(lex)
    if len(lists) > 1:
        fused = repo.rrf(lists, settings.RRF_K)
    else:
        fused = vec_results
    filtered = [c for c in fused if c['score'] >= settings.SIMILARITY_THRESHOLD or hybrid]
    return filtered[:top_k]
