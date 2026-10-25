"""Bounded retry helper."""
from __future__ import annotations


def retry(fn, attempts: int = 3):
    last = None
    for _ in range(attempts):
        result = fn()
        if result is not None:
            return result
        last = "no result"
    return None, last
