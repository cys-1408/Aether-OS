"""Rename/move tracking: preserve file identity across moves."""
from __future__ import annotations

import time

_cookie_map: dict[int, tuple[str, float]] = {}
TTL = 30.0


def record_moved_from(cookie: int, path: str) -> None:
    _cookie_map[cookie] = (path, time.monotonic())


def resolve_moved_to(cookie: int, new_path: str) -> str | None:
    entry = _cookie_map.pop(cookie, None)
    return entry[0] if entry else None


def sweep() -> None:
    import time as t
    now = t.monotonic()
    for k in [k for k, (_, ts) in _cookie_map.items() if now - ts > TTL]:
        _cookie_map.pop(k, None)
