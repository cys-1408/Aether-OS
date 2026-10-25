"""Presence rate limiting (per category)."""
from __future__ import annotations

import time

_last: dict[str, float] = {}
INTERVAL = 60.0


def allow(category: str) -> bool:
    now = time.monotonic()
    if now - _last.get(category, 0) < INTERVAL:
        return False
    _last[category] = now
    return True
