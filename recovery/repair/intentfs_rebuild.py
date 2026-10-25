"""Clear + queue full reindex (source files untouched)."""
from __future__ import annotations

import sqlite3
from pathlib import Path


def rebuild_all(root: str) -> dict:
    cleared = 0
    for db in Path(root).rglob(".local/share/aether/intentfs/intentfs.db"):
        with sqlite3.connect(db) as conn:
            cleared += conn.execute("SELECT COUNT(*) FROM files").fetchone()[0]
            conn.execute("DELETE FROM extracted_text")
            conn.execute("DELETE FROM files")
    return {"cleared": cleared, "reindex": "queued on next boot",
            "note": "index data only; user files untouched"}
