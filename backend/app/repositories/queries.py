from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models.query import Query
from typing import List

class QueryRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self, text: str, cleaned: str, embedding: list[float]) -> Query:
        q = Query(text=text, cleaned=cleaned, embedding=embedding)
        self.session.add(q)
        self.session.flush()
        return q

    def recent(self, limit: int = 20) -> List[Query]:
        res = self.session.execute(select(Query).order_by(Query.created_at.desc()).limit(limit))
        return list(res.scalars())
