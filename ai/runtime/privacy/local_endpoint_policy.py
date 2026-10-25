"""Enforce loopback-only inference endpoints."""
from __future__ import annotations

from aether_core.errors import IpcError


def enforce_bind(bind: str) -> str:
    if bind not in ("127.0.0.1", "localhost", "::1"):
        raise IpcError("E_POLICY", f"refusing non-loopback bind: {bind}")
    return "127.0.0.1"
