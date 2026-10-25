"""Remote providers are structurally denied in 1.0.0."""
from __future__ import annotations

from aether_core.errors import IpcError

REMOTE_PROVIDERS: list[str] = []  # none exist; keep it that way until a consent flow ships


def ensure_local_only(endpoint: str) -> str:
    if endpoint and not endpoint.startswith(("http://127.0.0.1", "http://localhost", "http://::1", "/")):
        raise IpcError("E_POLICY", "remote inference providers are disabled in 1.0.0")
    return endpoint
