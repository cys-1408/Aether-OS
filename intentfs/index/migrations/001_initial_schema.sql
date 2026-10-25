-- v1 initial schema (same as schema.sql baseline)
CREATE TABLE IF NOT EXISTS files (
    file_id TEXT PRIMARY KEY,
    path TEXT UNIQUE NOT NULL,
    filename TEXT NOT NULL,
    mime_type TEXT,
    size_bytes INTEGER,
    mtime REAL,
    content_hash TEXT,
    extractor_version TEXT,
    model_id TEXT,
    index_status TEXT NOT NULL DEFAULT 'pending',
    concepts TEXT,
    failure_reason TEXT,
    privacy_scope TEXT DEFAULT 'user-local',
    indexed_at TEXT,
    tombstoned INTEGER DEFAULT 0
);
CREATE TABLE IF NOT EXISTS extracted_text (
    file_id TEXT PRIMARY KEY REFERENCES files(file_id) ON DELETE CASCADE,
    text TEXT
);
CREATE INDEX IF NOT EXISTS idx_files_status ON files(index_status);
