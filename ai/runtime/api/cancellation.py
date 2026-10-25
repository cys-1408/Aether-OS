"""Cancellation registry for in-flight inference."""
from __future__ import annotations

import threading
from aether_core import CancellationToken

_registry: dict[str, CancellationToken] = {}
_lock = threading.Lock()


def register(request_id: str) -> CancellationToken:
    tok = CancellationToken()
    with _lock:
        _registry[request_id] = tok
    return tok


def cancel(request_id: str) -> bool:
    with _lock:
        tok = _registry.pop(request_id, None)
    if tok:
        tok.cancel()
        return True
    return False


def finish(request_id: str) -> None:
    with _lock:
        _registry.pop(request_id, None)
