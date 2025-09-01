from fastapi import APIRouter, Depends, Query as Q
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.repositories.queries import QueryRepository
from app.core.response import success

router = APIRouter()

@router.get('/queries/recent')
def recent_queries(limit: int = Q(20, ge=1, le=100), db: Session = Depends(get_db)):
    repo = QueryRepository(db)
    qs = repo.recent(limit)
    data = [{"id": str(q.id), "text": q.text, "created_at": q.created_at} for q in qs]
    return success({"items": data})
