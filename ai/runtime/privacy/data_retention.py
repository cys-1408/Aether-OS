"""Retention sweep for any cached AI data (real deletions)."""
from __future__ import annotations

import time
from pathlib import Path


def sweep(directory: Path, retention_days: int) -> int:
    if retention_days <= 0:
        return 0
    cutoff = time.time() - retention_days * 86400
    removed = 0
    for f in directory.rglob("*"):
        if f.is_file() and f.stat().st_mtime < cutoff:
            f.unlink(missing_ok=True)
            removed += 1
    return removed
