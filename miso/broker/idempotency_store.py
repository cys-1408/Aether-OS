"""Request-id dedupe with TTL."""
from __future__ import annotations

import time

TTL = 300


class IdempotencyStore:
    def __init__(self):
        self._seen: dict[str, tuple[float, dict]] = {}

    def seen(self, rid: str) -> bool:
        entry = self._seen.get(rid)
        if not entry:
            return False
        if time.monotonic() - entry[0] > TTL:
            del self._seen[rid]
            return False
        return True

    def result_of(self, rid: str) -> dict:
        return self._seen[rid][1]

    def store(self, rid: str, result: dict) -> None:
        if rid:
            self._seen[rid] = (time.monotonic(), result)
