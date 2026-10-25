"""Pin a model against idle unload."""
from __future__ import annotations

from model_registry import _db


def pin(model_id: str, pinned: bool) -> dict:
    conn = _db()
    cur = conn.execute("UPDATE models SET pinned=? WHERE model_id=?", (1 if pinned else 0, model_id))
    conn.commit()
    changed = cur.rowcount
    conn.close()
    return {"model_id": model_id, "pinned": pinned, "changed": changed}
