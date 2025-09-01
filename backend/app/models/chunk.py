from sqlalchemy import Column, Text, Integer, ForeignKey, JSON, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
import uuid
from app.db.base import Base

class Chunk(Base):
    __tablename__ = 'chunks'
    __table_args__ = {"extend_existing": True}
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id = Column(UUID(as_uuid=True), ForeignKey('documents.id', ondelete='CASCADE'), nullable=False)
    ordinal = Column(Integer, nullable=False)
    text = Column(Text, nullable=False)
    tokens = Column(Integer, nullable=False)
    page = Column(Integer)
    section = Column(Text)
    meta = Column(JSON, default=dict)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
