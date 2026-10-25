"""Timeout wrapper for backend calls."""
from __future__ import annotations

import threading


def with_timeout(fn, timeout_s: float):
    result: dict = {}

    def target():
        try:
            result["value"] = fn()
        except Exception as e:  # noqa: BLE001
            result["error"] = e

    t = threading.Thread(target=target, daemon=True)
    t.start()
    t.join(timeout_s)
    if t.is_alive():
        from aether_core.errors import IpcError
        raise IpcError("E_TIMEOUT", f"inference exceeded {timeout_s}s")
    if "error" in result:
        raise result["error"]
    return result.get("value")
