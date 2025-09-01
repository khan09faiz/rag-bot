# Simple Gemini RAG Backend

Minimal production-ready(ish) RAG backend using FastAPI + Postgres (pgvector) + Gemini (embeddings + chat) + LangChain.

## Features
- Ingestion of text or files (PDF, DOCX, HTML, TXT)
- Normalization + simple overlapping char-based chunking (approx token sized)
- Dedup via SHA256 of normalized full text
- Embeddings stored in pgvector (gemini-text-embedding-004, 768-dim)
- Hybrid retrieval (vector + lexical) with Reciprocal Rank Fusion
- Optional MMR diversification (function present, not wired by default)
- Streaming chat endpoint with inline citations ([Source n])
- Simple rate limiting + optional bearer token auth
- Structured JSON logging

## Quick Start

```bash
cp .env.example .env  # set GEMINI_API_KEY
docker-compose up --build
```
Navigate to http://localhost:8000/docs

## Endpoints
- GET /healthz
- POST /ingest (multipart or form text)
- POST /ingest/text (JSON)
- GET /ingest/{job_id}
- POST /search
- POST /chat (SSE stream)

## Example Search
```bash
curl -X POST http://localhost:8000/search -H 'Content-Type: application/json' \
  -d '{"query":"test", "top_k":5}'
```

## pgvector Setup (Supabase)
Enable the `vector` extension in the SQL editor:
```sql
create extension if not exists vector;
```
Run migrations/up.sql contents.

## Notes / Improvements
- Replace char-based chunking with token-aware logic
- Add proper async background worker for large files (RQ/Celery) if needed
- Add MMR step integration
- Add caching layer (Redis) if scaling

## License
MIT
