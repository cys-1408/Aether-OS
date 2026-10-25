-- IntentFS per-user index schema (v1)
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
CREATE TABLE IF NOT EXISTS schema_version (v INTEGER NOT NULL);
INSERT OR IGNORE INTO schema_version (v) VALUES (1);
CREATE INDEX IF NOT EXISTS idx_files_status ON files(index_status);
CREATE INDEX IF NOT EXISTS idx_files_name ON files(filename);
