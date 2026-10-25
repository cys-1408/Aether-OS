"""Typed client for apps to request capabilities (goes through broker)."""
from __future__ import annotations

import time

from aether_core.ipc import call
from aether_core.errors import IpcError
from aether_core import paths


def request(capability_id: str, params: dict, *, uid: int | None = None,
            timeout: float = 30.0) -> dict:
    request = {
        "request_id": f"app-{int(time.time()*1000)}",
        "capability_id": capability_id,
        "capability_version": "1.0.0",
        "requester": {"uid": uid if uid is not None else __import__("os").getuid(), "kind": "app"},
        "params": params,
        "issued_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
    }
    return call(paths.system_socket("broker"), "Broker.request", {"request": request}, timeout=timeout)


def capabilities() -> dict:
    return call(paths.system_socket("broker"), "Broker.capabilities", {}, timeout=5)
