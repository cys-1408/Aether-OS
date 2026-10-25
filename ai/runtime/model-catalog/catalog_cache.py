"""Catalog cache with TTL (re-validated on load)."""
from __future__ import annotations

import time
from pathlib import Path

from aether_core import paths

CACHE = paths.SYSTEM_CACHE_DIR if hasattr(paths, "SYSTEM_CACHE_DIR") else Path("/var/cache/aether")
CACHE_FILE = CACHE / "catalog-cache.json"
TTL_S = 3600


def get_cached(loader) -> dict:
    if CACHE_FILE.exists() and time.time() - CACHE_FILE.stat().st_mtime < TTL_S:
        try:
            return json.loads(CACHE_FILE.read_text())
        except (json.JSONDecodeError, OSError):
            pass
    data = loader()
    CACHE.mkdir(parents=True, exist_ok=True)
    CACHE_FILE.write_text(json.dumps(data))
    return data


import json  # noqa: E402
