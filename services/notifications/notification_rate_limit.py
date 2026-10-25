"""Token bucket per (category,key): suppress unchanged-condition spam."""
from __future__ import annotations

import time
from collections import defaultdict

_MIN_INTERVAL = 60.0
_last: dict[tuple, float] = defaultdict(float)


def allow(category: str, key: str = "", min_interval: float = _MIN_INTERVAL) -> dict:
    now = time.monotonic()
    slot = (category, key)
    if now - _last[slot] < min_interval:
        return {"allowed": False, "retry_in_s": round(min_interval - (now - _last[slot]), 1)}
    _last[slot] = now
    return {"allowed": True}
