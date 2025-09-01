from fastapi import FastAPI
from sqlalchemy import text
from app.db.session import engine
from app.db.base import Base
from app.core.config import settings
from app.core.cors import add_cors
from app.api import health, ingest, search, chat, queries, debug

app = FastAPI(title="Simple Gemini RAG", version="0.2.0")
add_cors(app)

app.include_router(health.router)
app.include_router(ingest.router)
app.include_router(search.router)
app.include_router(chat.router)
app.include_router(queries.router)
app.include_router(debug.router)

@app.on_event("startup")
def _startup():
    with engine.begin() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        # Ensure expected JSON columns exist to avoid UndefinedColumn errors
        try:
            conn.execute(text("ALTER TABLE documents ADD COLUMN IF NOT EXISTS metadata jsonb DEFAULT '{}'::jsonb"))
        except Exception as e:
            # ignore if permission denied (e.g., limited role); table may already have column
            print(f"[STARTUP] documents metadata ensure skipped: {e}")
        try:
            conn.execute(text("ALTER TABLE chunks ADD COLUMN IF NOT EXISTS meta jsonb DEFAULT '{}'::jsonb"))
        except Exception as e:
            print(f"[STARTUP] chunks meta ensure skipped: {e}")
        try:
            conn.execute(text("ALTER TABLE chunks ADD COLUMN IF NOT EXISTS created_at timestamptz DEFAULT now()"))
        except Exception as e:
            print(f"[STARTUP] chunks created_at ensure skipped: {e}")
        # create tables if not exist (simple bootstrap)
        Base.metadata.create_all(bind=engine)

@app.get('/')
def root():
    return {"message": "RAG backend running"}
