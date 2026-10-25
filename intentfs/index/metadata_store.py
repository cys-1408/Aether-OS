"""SQLite metadata store (WAL, transactions, tombstones)."""
from __future__ import annotations

import json
import sqlite3
import time
from pathlib import Path

from aether_core.errors import AetherError

SCHEMA = Path(__file__).resolve().parent / "schema.sql"


class MetadataStore:
    def __init__(self, db_path: Path):
        db_path.parent.mkdir(parents=True, exist_ok=True)
        self.db_path = db_path
        self._init()

    def _init(self) -> None:
        conn = sqlite3.connect(self.db_path)
        conn.executescript(SCHEMA.read_text())
        conn.commit()
        conn.close()

    def _conn(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.execute("PRAGMA journal_mode=WAL")
        conn.row_factory = sqlite3.Row
        return conn

    def upsert(self, record: dict) -> None:
        """Transactional metadata write (concepts exactly-3 enforced for ready)."""
        status = record.get("index_status", "pending")
        concepts = record.get("concepts")
        if status == "ready":
            if not isinstance(concepts, list) or len(concepts) != 3 or len(set(concepts)) != 3:
                raise AetherError("E_CONCEPTS", "ready records must carry exactly 3 distinct concepts")
        with self._conn() as conn:
            with conn:
                conn.execute("""INSERT INTO files (file_id,path,filename,mime_type,size_bytes,mtime,
                                content_hash,extractor_version,index_status,concepts,failure_reason,indexed_at)
                                VALUES (?,?,?,?,?,?,?,?,?,?,?,?)
                                ON CONFLICT(path) DO UPDATE SET
                                  file_id=excluded.file_id, filename=excluded.filename,
                                  mime_type=excluded.mime_type, size_bytes=excluded.size_bytes,
                                  mtime=excluded.mtime, content_hash=excluded.content_hash,
                                  extractor_version=excluded.extractor_version,
                                  index_status=excluded.index_status, concepts=excluded.concepts,
                                  failure_reason=excluded.failure_reason, indexed_at=excluded.indexed_at,
                                  tombstoned=0""",
                             (record.get("file_id"), record.get("path"), record.get("filename"),
                              record.get("mime_type"), record.get("size_bytes"), record.get("mtime"),
                              record.get("content_hash"), record.get("extractor_version"),
                              status, json.dumps(concepts) if concepts else None,
                              record.get("failure_reason"),
                              time.strftime("%Y-%m-%dT%H:%M:%S%z")))
            if record.get("extracted_text"):
                conn.execute("""INSERT INTO extracted_text (file_id, text) VALUES (?, ?)
                                ON CONFLICT(file_id) DO UPDATE SET text=excluded.text""",
                             (record.get("file_id"), record["extracted_text"][:2000]))

    def get_by_path(self, path: str) -> dict | None:
        with self._conn() as conn:
            row = conn.execute("SELECT * FROM files WHERE path=? AND tombstoned=0", (path,)).fetchone()
        return self._to_record(row) if row else None

    def tombstone(self, path: str) -> None:
        with self._conn() as conn:
            with conn:
                conn.execute("UPDATE files SET tombstoned=1 WHERE path=?", (path,))

    def clear_all(self) -> int:
        """Index-only deletion. NEVER touches source files (paths are data, not handles)."""
        with self._conn() as conn:
            with conn:
                n = conn.execute("SELECT COUNT(*) FROM files").fetchone()[0]
                conn.execute("DELETE FROM extracted_text")
                conn.execute("DELETE FROM files")
        return n

    @staticmethod
    def _to_record(row) -> dict:
        rec = dict(row)
        rec["concepts"] = json.loads(rec["concepts"]) if rec.get("concepts") else None
        rec.pop("tombstoned", None)
        return rec
