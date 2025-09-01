from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models.document import Document
from typing import Optional
from .base import BaseRepository

class DocumentRepository(BaseRepository):
    def __init__(self, session: Session):
        super().__init__(session, Document)

    def get_by_hash(self, h: str) -> Optional[Document]:
        res = self.session.execute(select(Document).where(Document.content_hash == h))
        return res.scalar_one_or_none()

    def create_document(self, title: str, text_hash: str, mime_type: str, metadata: dict, source_uri: str | None) -> Document:
        # Model column is named 'meta'
        return super().create(title=title, content_hash=text_hash, mime_type=mime_type, meta=metadata, source_uri=source_uri)
