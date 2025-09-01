from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.repositories.documents import DocumentRepository
from app.repositories.embeddings import EmbeddingRepository
from app.utils.hash import content_hash
from app.utils.normalize import normalize_text
from app.utils.chunking import chunk_text
from app.models.chunk import Chunk
from app.core.config import settings
from app.services.embedding_service import embed_texts
from app.core.auth import bearer_auth
import logging

router = APIRouter(prefix="/debug", tags=["debug"], dependencies=[Depends(bearer_auth)])
logger = logging.getLogger("debug")

@router.post('/ingest_text')
def debug_ingest_text(text: str, title: str = "Debug Doc", db: Session = Depends(get_db)):
    text_norm = normalize_text(text or "")
    h = content_hash(text_norm)
    doc_repo = DocumentRepository(db)
    if doc_repo.get_by_hash(h):
        return {"status": "duplicate"}
    doc = doc_repo.create_document(title, h, 'text/plain', {}, None)
    raw_chunks = chunk_text(text_norm, settings.CHUNK_TOKENS, settings.CHUNK_OVERLAP_PCT)
    chunk_ids = []
    texts = []
    for idx, (c_text, tokens) in enumerate(raw_chunks):
        ch = Chunk(document_id=doc.id, ordinal=idx, text=c_text, tokens=tokens)
        db.add(ch)
        db.flush()
        chunk_ids.append(str(ch.id))
        texts.append(c_text)
    db.commit()
    vectors = embed_texts(texts) if texts else []
    if vectors:
        emb_repo = EmbeddingRepository(db)
        emb_repo.bulk_upsert(chunk_ids, vectors, settings.GEMINI_EMBED_MODEL, len(vectors[0]))
        db.commit()
    logger.info(f"[DEBUG_INGEST] doc={doc.id} chunks={len(chunk_ids)} vectors={len(vectors)}")
    return {"status": "ok", "doc_id": str(doc.id), "chunks": len(chunk_ids), "vectors": len(vectors)}
