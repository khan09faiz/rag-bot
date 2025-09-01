from sqlalchemy import Column, Text, DateTime, func, JSON, String, UUID
from sqlalchemy.dialects.postgresql import UUID
import uuid
from app.db.base import Base

class Document(Base):
    __tablename__ = 'documents'
    __table_args__ = {"extend_existing": True}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(Text, nullable=False)
    source_uri = Column(Text)
    mime_type = Column(Text)
    content_hash = Column(String, unique=True, nullable=False)
    # Map attribute 'meta' to existing physical column 'metadata' if that is what exists.
    # If the column in DB is named 'metadata', this mapping works; if it's already 'meta', adjust accordingly.
    meta = Column('metadata', JSON, default=dict)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    owner_id = Column(UUID(as_uuid=True), nullable=True)
