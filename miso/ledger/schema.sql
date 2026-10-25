-- Action Ledger schema v1 (append-oriented, hash-chained)
CREATE TABLE IF NOT EXISTS entries (
    entry_id TEXT PRIMARY KEY,
    prev_hash TEXT,
    entry_hash TEXT,
    timestamp TEXT NOT NULL,
    uid INTEGER NOT NULL,
    payload TEXT NOT NULL,        -- redacted JSON (request/plan/result/decision)
    status TEXT,
    result TEXT,
    verified INTEGER,
    retention_category TEXT DEFAULT 'user-action'
);
CREATE TABLE IF NOT EXISTS schema_version (v INTEGER NOT NULL);
INSERT OR IGNORE INTO schema_version (v) VALUES (1);
CREATE INDEX IF NOT EXISTS idx_entries_uid_ts ON entries(uid, timestamp);
