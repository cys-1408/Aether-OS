"""Disk quota enforcement for the model store."""
from __future__ import annotations

from pathlib import Path


def store_usage_bytes(store_dir: Path) -> int:
    return sum(f.stat().st_size for f in store_dir.rglob("*") if f.is_file())


def within_quota(store_dir: Path, quota_mb: int) -> bool:
    if quota_mb <= 0:
        return True
    return store_usage_bytes(store_dir) <= quota_mb * 1024 * 1024
