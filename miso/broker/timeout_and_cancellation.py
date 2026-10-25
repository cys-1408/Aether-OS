"""Timeout + cancellation wrappers for dispatch."""
from __future__ import annotations

import threading


def with_timeout(fn, timeout_s: float):
    box: dict = {}

    def target():
        try:
            box["value"] = fn()
        except Exception as e:  # noqa: BLE001
            box["error"] = e

    t = threading.Thread(target=target, daemon=True)
    t.start()
    t.join(timeout_s)
    if t.is_alive():
        from aether_core.errors import IpcError
        raise IpcError("E_TIMEOUT", f"capability exceeded {timeout_s}s")
    if "error" in box:
        raise box["error"]
    return box.get("value")
