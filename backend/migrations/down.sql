DROP INDEX IF EXISTS embeddings_cosine_idx;
DROP INDEX IF EXISTS chunks_fts_idx;
DROP INDEX IF EXISTS chunks_document_ordinal_idx;
DROP INDEX IF EXISTS documents_hash_idx;
DROP INDEX IF EXISTS upload_jobs_status_idx;

DROP TABLE IF EXISTS embeddings;
DROP TABLE IF EXISTS chunks;
DROP TABLE IF EXISTS documents;
DROP TABLE IF EXISTS upload_jobs;
