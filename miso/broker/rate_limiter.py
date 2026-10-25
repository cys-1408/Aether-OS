"""Token bucket per (uid, capability)."""
from __future__ import annotations

import time
from collections import defaultdict

_BURST = 10
_REFILL_S = 6.0


class RateLimiter:
    def __init__(self):
        self._buckets: dict[tuple, float] = defaultdict(lambda: _BURST)
        self._last: dict[tuple, float] = defaultdict(lambda: time.monotonic())

    def allow(self, uid: int, capability: str) -> bool:
        key = (uid, capability)
        now = time.monotonic()
        elapsed = now - self._last[key]
        self._last[key] = now
        self._buckets[key] = min(_BURST, self._buckets[key] + elapsed / _REFILL_S)
        if self._buckets[key] >= 1:
            self._buckets[key] -= 1
            return True
        return False
