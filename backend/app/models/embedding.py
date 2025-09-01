from sqlalchemy import Column, Text, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.dialects import postgresql
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

class Embedding(Base):
    __tablename__ = 'embeddings'
    chunk_id = Column(UUID(as_uuid=True), ForeignKey('chunks.id', ondelete='CASCADE'), primary_key=True)
    model_name = Column(Text, nullable=False, default='gemini-text-embedding-004')
    dim = Column(Integer, nullable=False, default=768)
    embedding = Column(Vector(768), nullable=False)
