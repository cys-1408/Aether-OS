"""Integrity-check installed models; remove corrupted ones."""
from __future__ import annotations

import hashlib
import json
import sqlite3
from pathlib import Path


def remove_broken(root: str) -> dict:
    db = Path(root) / "var/lib/aether/runtime/models.db"
    if not db.exists():
        return {"removed": [], "reason": "no model registry"}
    removed = []
    with sqlite3.connect(db) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute("SELECT model_id, sha256 FROM models WHERE state='installed'").fetchall()
        for r in rows:
            files = list((Path(root) / "var/lib/aether/../..").rglob(f"{r['model_id']}*"))
            files = [f for f in Path(root).rglob(r["model_id"]) if f.is_file()]
            for f in files:
                h = hashlib.sha256()
                with open(f, "rb") as fh:
                    for chunk in iter(lambda: fh.read(1 << 20), b""):
                        h.update(chunk)
                if r["sha256"] and h.hexdigest() != r["sha256"]:
                    f.unlink()
                    conn.execute("UPDATE models SET state='removed' WHERE model_id=?", (r["model_id"],))
                    removed.append(r["model_id"])
        conn.commit()
    return {"removed": removed}
