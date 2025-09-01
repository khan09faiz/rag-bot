from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.core.config import settings
from app.repositories.documents import DocumentRepository
from app.repositories.embeddings import EmbeddingRepository
from app.repositories.search import SearchRepository
from app.services.embedding_service import embed_texts, embed_query
from app.utils.normalize import normalize_text
from app.utils.chunking import chunk_text
from app.utils.hash import content_hash
from app.models.chunk import Chunk
from app.core.auth import bearer_auth
import uuid

router = APIRouter(prefix="/debug", tags=["debug"], dependencies=[Depends(bearer_auth)])

@router.post('/ingest-sync')
def ingest_sync(text: str, title: str = "Untitled", db: Session = Depends(get_db)):
    """Synchronous ingestion (text only) for rapid troubleshooting.
    Returns created document/chunk counts and embedding stats immediately.
    """
    if not text.strip():
        raise HTTPException(400, "Empty text")
    clean = normalize_text(text)
    h = content_hash(clean)
    doc_repo = DocumentRepository(db)
    existing = doc_repo.get_by_hash(h)
    if existing:
        return {"status": "duplicate", "document_id": str(existing.id)}
    doc = doc_repo.create_document(title, h, 'text/plain', {}, None)
    raw_chunks = chunk_text(clean, settings.CHUNK_TOKENS, settings.CHUNK_OVERLAP_PCT)
    chunk_models = []
    texts = []
    for idx, (c_text, tokens) in enumerate(raw_chunks):
        ch = Chunk(document_id=doc.id, ordinal=idx, text=c_text, tokens=tokens)
        db.add(ch)
        db.flush()
        chunk_models.append(ch)
        texts.append(c_text)
    db.commit()
    vectors = embed_texts(texts) if texts else []
    if vectors:
        emb_repo = EmbeddingRepository(db)
        emb_repo.bulk_upsert([str(c.id) for c in chunk_models], vectors, settings.GEMINI_EMBED_MODEL, len(vectors[0]))
        db.commit()
    return {"status": "ok", "document_id": str(doc.id), "chunks": len(chunk_models), "embeddings": len(vectors)}

@router.get('/search')
def debug_search(q: str, top_k: int = 5, db: Session = Depends(get_db)):
    vec = embed_query(q)
    repo = SearchRepository(db)
    results, stats = repo.hybrid_retrieve(
        query=q,
        query_embedding=vec,
        top_k=top_k,
        use_lexical=True,
        rrf_k=settings.RRF_K,
        mmr_lambda=settings.MMR_LAMBDA,
        final_k=min(top_k, settings.TOP_M_CONTEXT),
        threshold=settings.SIMILARITY_THRESHOLD,
    )
    return {"results": results, "stats": stats}
