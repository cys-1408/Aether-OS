"""Tombstone policy: mark deleted, purge after retention."""
from __future__ import annotations


def purge_before(store, days: int) -> int:
    import sqlite3
    cutoff = time.strftime("%Y-%m-%dT%H:%M:%S%z", time.gmtime(time.time() - days * 86400))
    with sqlite3.connect(store.db_path) as conn:
        cur = conn.execute("DELETE FROM files WHERE tombstoned=1 AND indexed_at < ?", (cutoff,))
        return cur.rowcount


import time  # noqa: E402
