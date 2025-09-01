from fastapi import APIRouter, UploadFile, File, Form, Depends, BackgroundTasks, HTTPException
from sqlalchemy.orm import Session
from pathlib import Path
import uuid, shutil, asyncio
from app.core.config import settings
from app.db.session import get_db, SessionLocal
from app.utils.text_extract import extract_text
from app.utils.normalize import normalize_text
from app.utils.chunking import chunk_text
from app.utils.hash import content_hash
from app.models.job import UploadJob
from app.models.chunk import Chunk
from app.repositories.documents import DocumentRepository
from app.repositories.embeddings import EmbeddingRepository
from app.schemas.ingest import IngestTextRequest, IngestResponse
from app.core.response import success
from app.services.embedding_service import embed_texts
from app.core.auth import bearer_auth
from app.utils.clean import clean_for_embedding
import logging

logger = logging.getLogger("ingest")

router = APIRouter()

async def _embed_chunks(embeddings, texts: list[str]):
    return embeddings.embed_documents(texts)

@router.post('/ingest', response_model=IngestResponse, dependencies=[Depends(bearer_auth)])
def ingest(background: BackgroundTasks, db: Session = Depends(get_db), file: UploadFile | None = File(None), text: str | None = Form(None), title: str | None = Form(None)):
    if not file and not text:
        raise HTTPException(400, 'Provide file or text')

    # Persist initial job with request-scoped session
    job = UploadJob(status='queued')
    db.add(job)
    db.commit()
    job_id = str(job.id)

    # For file uploads, persist temp copy path to pass to background task
    tmp_path: Path | None = None
    orig_filename: str | None = None
    content_type: str | None = None
    if file:
        tmp_dir = Path('/tmp')
        tmp_dir.mkdir(parents=True, exist_ok=True)
        tmp_path = tmp_dir / f"upload_{uuid.uuid4()}_{file.filename}"
        with tmp_path.open('wb') as out:
            shutil.copyfileobj(file.file, out)
        orig_filename = file.filename
        content_type = file.content_type

    def process(job_id: str, tmp_path: Path | None, orig_filename: str | None, content_type: str | None, inline_text: str | None, inline_title: str | None):
        session = SessionLocal()
        try:
            job_row = session.get(UploadJob, uuid.UUID(job_id))
            if not job_row:
                return
            job_row.status = 'running'
            session.commit()
            if tmp_path:
                extracted, mime = extract_text(tmp_path, content_type)
                full_text = extracted
                doc_title = inline_title or orig_filename or 'Untitled'
            else:
                full_text = inline_text or ''
                mime = 'text/plain'
                doc_title = inline_title or 'Untitled'
            logger.info(f"[INGEST] job={job_id} bytes={len(full_text)} title={doc_title}")
            full_text = normalize_text(full_text)
            h = content_hash(full_text)
            doc_repo = DocumentRepository(session)
            existing = doc_repo.get_by_hash(h)
            if existing:
                logger.info(f"[INGEST] job={job_id} duplicate document hash; skipping")
                job_row.status = 'done'
                session.commit()
                return
            document = doc_repo.create_document(doc_title, h, mime, {}, None)
            logger.info(f"[INGEST] job={job_id} document_id={document.id}")
            # chunk
            raw_chunks = chunk_text(full_text, settings.CHUNK_TOKENS, settings.CHUNK_OVERLAP_PCT)
            chunk_models = []
            texts = []
            for idx, (c_text, tokens) in enumerate(raw_chunks):
                ch = Chunk(document_id=document.id, ordinal=idx, text=c_text, tokens=tokens)
                session.add(ch)
                session.flush()
                chunk_models.append(ch)
                texts.append(c_text)
            logger.info(f"[INGEST] job={job_id} chunks={len(chunk_models)}")
            # commit document + chunks first so they persist even if embedding fails
            session.commit()
            try:
                vectors = embed_texts(texts) if texts else []
                if vectors:
                    emb_repo = EmbeddingRepository(session)
                    emb_repo.bulk_upsert([str(c.id) for c in chunk_models], vectors, settings.GEMINI_EMBED_MODEL, len(vectors[0]))
                session.commit()
                job_row.status = 'done'
                logger.info(f"[INGEST] job={job_id} embeddings={len(vectors)} done")
            except Exception as embed_err:
                print(f"[EMBED_ERROR] job={job_id} error={embed_err}", flush=True)
                job_row.status = 'partial'
                job_row.error = f"Embedding failed: {embed_err}"
                session.commit()
        except Exception as e:
            # basic stderr logging (could wire structured logger later)
            try:
                print(f"[INGEST_ERROR] job={job_id} error={e}", flush=True)
            except Exception:
                pass
            if 'session' in locals():
                job_row = session.get(UploadJob, uuid.UUID(job_id))
                if job_row:
                    job_row.status = 'error'
                    job_row.error = str(e)
                    session.commit()
        finally:
            session.close()
            # cleanup temp file
            if tmp_path and tmp_path.exists():
                try:
                    tmp_path.unlink()
                except Exception:
                    pass

    background.add_task(process, job_id, tmp_path, orig_filename, content_type, text, title)
    return success({"job_id": job_id})

@router.post('/ingest/text', response_model=IngestResponse, dependencies=[Depends(bearer_auth)])
def ingest_text(payload: IngestTextRequest, background: BackgroundTasks, db: Session = Depends(get_db)):
    return ingest(background, db, None, payload.text, payload.title)

@router.get('/ingest/{job_id}')
def get_job(job_id: str, db: Session = Depends(get_db)):
    from sqlalchemy import select
    from app.models.job import UploadJob
    res = db.execute(select(UploadJob).where(UploadJob.id == uuid.UUID(job_id)))
    job = res.scalar_one_or_none()
    if not job:
        raise HTTPException(404, 'Not found')
    return {"id": str(job.id), "status": job.status, "error": job.error, "started_at": job.started_at, "finished_at": job.finished_at}
