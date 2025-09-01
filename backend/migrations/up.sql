CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS pgcrypto; -- for gen_random_uuid()

CREATE TABLE documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title TEXT NOT NULL,
    source_uri TEXT,
    mime_type TEXT,
    content_hash TEXT UNIQUE NOT NULL,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    owner_id UUID
);

CREATE TABLE chunks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    ordinal INTEGER NOT NULL,
    text TEXT NOT NULL,
    tokens INTEGER NOT NULL,
    page INTEGER,
    section TEXT,
    metadata JSONB DEFAULT '{}',
    UNIQUE(document_id, ordinal)
);

CREATE TABLE embeddings (
    chunk_id UUID PRIMARY KEY REFERENCES chunks(id) ON DELETE CASCADE,
    model_name TEXT NOT NULL DEFAULT 'gemini-text-embedding-004',
    dim INTEGER NOT NULL DEFAULT 768,
    embedding vector(768) NOT NULL
);

CREATE TABLE upload_jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    status TEXT NOT NULL CHECK (status IN ('queued','running','done','error')),
    error TEXT,
    started_at TIMESTAMPTZ,
    finished_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX embeddings_cosine_idx ON embeddings USING ivfflat (embedding vector_cosine_ops) WITH (lists = 200);
CREATE INDEX chunks_fts_idx ON chunks USING gin (to_tsvector('english', text));
CREATE INDEX chunks_document_ordinal_idx ON chunks (document_id, ordinal);
CREATE INDEX documents_hash_idx ON documents (content_hash);
CREATE INDEX upload_jobs_status_idx ON upload_jobs (status, created_at);
