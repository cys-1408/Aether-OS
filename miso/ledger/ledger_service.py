"""Append-oriented ledger service (hash-chained, redacted, per-user query)."""
from __future__ import annotations

import hashlib
import json
import sqlite3
import time
import uuid
from pathlib import Path

from aether_core import paths
from aether_core.config import atomic_write_json
from aether_core.errors import IpcError

DB = paths.SYSTEM_STATE_DIR / "ledger" / "ledger.db"
RETENTION_DAYS = 90


class LedgerService:
    def __init__(self):
        DB.parent.mkdir(parents=True, exist_ok=True)
        self._init()

    def _init(self) -> None:
        conn = sqlite3.connect(DB)
        conn.executescript((Path(__file__).resolve().parent / "schema.sql").read_text())
        conn.commit()
        conn.close()

    def append(self, entry: dict) -> str:
        entry_id = entry.get("entry_id") or f"le-{uuid.uuid4().hex[:12]}"
        with sqlite3.connect(DB) as conn:
            with conn:
                prev = conn.execute(
                    "SELECT entry_hash FROM entries ORDER BY rowid DESC LIMIT 1").fetchone()
                prev_hash = prev[0] if prev else None
                blob = json.dumps(entry.get("payload", {}), sort_keys=True, default=str)
                entry_hash = hashlib.sha256(((prev_hash or "") + blob).encode()).hexdigest()
                conn.execute("""INSERT INTO entries (entry_id, prev_hash, entry_hash, timestamp,
                                uid, payload, status, result, verified, retention_category)
                                VALUES (?,?,?,?,?,?,?,?,?,?)""",
                             (entry_id, prev_hash, entry_hash,
                              entry.get("timestamp") or time.strftime("%Y-%m-%dT%H:%M:%S%z"),
                              int(entry.get("uid", 0)),
                              blob, entry.get("status"),
                              json.dumps(entry.get("result"), default=str) if entry.get("result") else None,
                              1 if entry.get("verified") else 0,
                              entry.get("retention_category", "user-action")))
        return entry_id

    def query(self, uid: int, *, limit: int = 50, capability: str | None = None) -> dict:
        with sqlite3.connect(DB) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(
                "SELECT * FROM entries WHERE uid=? ORDER BY rowid DESC LIMIT ?",
                (uid, max(1, min(200, limit)))).fetchall()
        entries = []
        for r in rows:
            payload = json.loads(r["payload"])
            if capability and capability not in json.dumps(payload):
                continue
            entries.append({"entry_id": r["entry_id"], "timestamp": r["timestamp"],
                            "request": payload, "status": r["status"],
                            "result": json.loads(r["result"]) if r["result"] else None,
                            "verified": bool(r["verified"]),
                            "entry_hash": r["entry_hash"][:16]})
        return {"entries": entries}

    def verify_chain(self) -> dict:
        with sqlite3.connect(DB) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute("SELECT * FROM entries ORDER BY rowid").fetchall()
        prev = None
        for r in rows:
            expect = hashlib.sha256(((prev or "") + r["payload"]).encode()).hexdigest()
            if expect != r["entry_hash"]:
                return {"chain_ok": False, "broken_at": r["entry_id"]}
            prev = r["entry_hash"]
        return {"chain_ok": True, "entries": len(rows)}

    def clear(self, uid: int) -> dict:
        with sqlite3.connect(DB) as conn:
            with conn:
                n = conn.execute("DELETE FROM entries WHERE uid=? AND retention_category='user-action'",
                                 (uid,)).rowcount
        return {"cleared": n, "note": "protected system entries retained"}

    def sweep(self) -> int:
        with sqlite3.connect(DB) as conn:
            with conn:
                cur = conn.execute("DELETE FROM entries WHERE timestamp < ?",
                                   (time.strftime("%Y-%m-%dT%H:%M:%S%z",
                                                  time.gmtime(time.time() - RETENTION_DAYS * 86400)),))
                return cur.rowcount
