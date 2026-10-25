"""Registry schema migrations (forward-only)."""
from __future__ import annotations

from model_registry import _db


def migrate() -> int:
    conn = _db()
    version = 1
    conn.execute("CREATE TABLE IF NOT EXISTS schema_version (v INTEGER)")
    row = conn.execute("SELECT v FROM schema_version").fetchone()
    if not row:
        conn.execute("INSERT INTO schema_version VALUES (?)", (version,))
    conn.commit()
    conn.close()
    return version
