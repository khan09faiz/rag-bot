from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.search import SearchRequest
from app.schemas.common import ChunkCandidate
from app.core.response import success
from app.services.retrieval_service import retrieve

router = APIRouter()

@router.post('/search')
def search(payload: SearchRequest, db: Session = Depends(get_db)):

    from time import perf_counter
    t0 = perf_counter()
    final = retrieve(payload.query, db, payload.top_k, payload.hybrid)
    t_ms = int((perf_counter() - t0) * 1000)
    candidates = [ChunkCandidate(id=c['id'], score=c['score'], doc_title=c['title'], page=c['page'], section=c['section'], snippet=c['text'][:300]).model_dump() for c in final]
    return success({"candidates": candidates, "timings": {"retrieve_ms": t_ms}})
