"""Installed-model registry (sqlite, WAL)."""
from __future__ import annotations

import sqlite3
import time
from pathlib import Path

from aether_core import paths
from aether_core.config import atomic_write_json
from aether_core.errors import IpcError

DB = paths.SYSTEM_STATE_DIR / "runtime" / "models.db"


def _db() -> sqlite3.Connection:
    DB.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB)
    conn.execute("""CREATE TABLE IF NOT EXISTS models (
        model_id TEXT PRIMARY KEY, name TEXT, repo TEXT, file TEXT,
        size_bytes INTEGER, state TEXT, sha256 TEXT, license TEXT,
        installed_at TEXT, last_used TEXT, pinned INTEGER DEFAULT 0)""")
    return conn


class ModelRegistry:
    def list(self) -> dict:
        conn = _db()
        rows = conn.execute("SELECT model_id,name,repo,file,size_bytes,state,license,installed_at,pinned FROM models").fetchall()
        conn.close()
        return {"models": [
            {"model_id": r[0], "name": r[1], "repo": r[2], "file": r[3],
             "size_gb": round(r[4] / 1e9, 2) if r[4] else None, "state": r[5],
             "license": r[6], "installed_at": r[7], "pinned": bool(r[8])} for r in rows]}

    def upsert(self, model: dict, size_bytes: int, sha256: str, state: str) -> None:
        conn = _db()
        conn.execute("""INSERT INTO models (model_id,name,repo,file,size_bytes,state,sha256,license,installed_at)
                        VALUES (?,?,?,?,?,?,?,?,?)
                        ON CONFLICT(model_id) DO UPDATE SET state=?, sha256=?, size_bytes=?""",
                     (model["model_id"], model["name"], model["repo"], model["file"],
                      size_bytes, state, sha256, model.get("license"),
                      time.strftime("%Y-%m-%dT%H:%M:%S%z"), state, sha256, size_bytes))
        conn.commit()
        conn.close()

    def remove(self, model_id: str) -> dict:
        conn = _db()
        row = conn.execute("SELECT file, pinned, state FROM models WHERE model_id=?", (model_id,)).fetchone()
        if not row:
            raise IpcError("E_NOT_FOUND", f"model {model_id} not installed")
        if row[1]:
            raise IpcError("E_PINNED", "model is pinned — unpin first")
        conn.execute("DELETE FROM models WHERE model_id=?", (model_id,))
        conn.commit()
        conn.close()
        return {"removed": model_id, "state_was": row[2]}
