from typing import Type, Any, Optional, List, Dict
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.core.errors import NotFoundError

class BaseRepository:
    def __init__(self, session: Session, model: Type[Any]):
        self.session = session
        self.model = model

    def get(self, id: Any):
        obj = self.session.get(self.model, id)
        if not obj:
            raise NotFoundError()
        return obj

    def list(self, offset: int = 0, limit: int = 50) -> List[Any]:
        stmt = select(self.model).offset(offset).limit(limit)
        return list(self.session.execute(stmt).scalars().all())

    def create(self, **kwargs) -> Any:
        obj = self.model(**kwargs)
        self.session.add(obj)
        self.session.flush()
        return obj

    def delete(self, id: Any) -> None:
        obj = self.get(id)
        self.session.delete(obj)
        self.session.flush()
