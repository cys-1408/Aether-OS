"""Package rollback from the transaction journal."""
from __future__ import annotations

import sqlite3
import subprocess
from pathlib import Path


def rollback_last(root: str) -> dict:
    db = Path(root) / "var/lib/aether/pm/transactions.db"
    if not db.exists():
        return {"rolled_back": False, "reason": "no transaction journal"}
    with sqlite3.connect(db) as conn:
        row = conn.execute("SELECT packages FROM transactions WHERE result='ok' ORDER BY id DESC LIMIT 1").fetchone()
    if not row:
        return {"rolled_back": False, "reason": "no completed transactions"}
    out = subprocess.run(["arch-chroot", root, "pacman", "-R", "--noconfirm", *row[0].split()],
                         capture_output=True, text=True, timeout=1800)
    return {"rolled_back": out.returncode == 0, "packages": row[0]}
