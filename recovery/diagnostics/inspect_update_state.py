"""Update journal inspection."""
from __future__ import annotations

import sqlite3
from pathlib import Path


def last_transactions(root: str) -> list[dict]:
    db = Path(root) / "var/lib/aether/pm/transactions.db"
    if not db.exists():
        return []
    with sqlite3.connect(db) as conn:
        rows = conn.execute("SELECT ts, action, result FROM transactions ORDER BY id DESC LIMIT 10").fetchall()
    return [{"ts": r[0], "action": r[1], "result": r[2]} for r in rows]
