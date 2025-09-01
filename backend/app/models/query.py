from sqlalchemy import Column, Text, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
import uuid
from app.db.base import Base
try:
    from pgvector.sqlalchemy import Vector
except ImportError:
    from sqlalchemy import types as _types
    class Vector(_types.TypeDecorator):
        impl = _types.ARRAY(_types.Float)
        cache_ok = True
        def __init__(self, dim: int):
            super().__init__()
            self.dim = dim

from app.core.config import settings

class Query(Base):
    __tablename__ = 'queries'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    text = Column(Text, nullable=False)
    cleaned = Column(Text, nullable=False)
    embedding = Column(Vector(settings.EMBED_DIM), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
