from sqlalchemy import Column, Text, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
import uuid
from app.db.base import Base

class UploadJob(Base):
    __tablename__ = 'upload_jobs'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    status = Column(Text, nullable=False, default='queued')
    error = Column(Text)
    started_at = Column(DateTime(timezone=True))
    finished_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
