"""Shared bootstrap for installer modules.

Puts the shared ``aether_core`` library (owned per CONVENTIONS.md §3) on
sys.path when it is present in the source tree and exposes result helpers
with identical semantics to ``aether_core.result`` so installer modules stay
self-contained on systems where the shared package is not installed.
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

_LIBAETHER = REPO_ROOT / "libraries" / "libaether-core" / "python"
if _LIBAETHER.is_dir() and str(_LIBAETHER) not in sys.path:
    sys.path.insert(0, str(_LIBAETHER))


def ok(value) -> dict:
    """Result envelope: success."""
    return {"ok": True, "value": value}


def err(code: str, message: str, *, retriable: bool = False, details=None) -> dict:
    """Result envelope: failure (matches aether_core.result.err shape)."""
    return {
        "ok": False,
        "error": {
            "code": code,
            "message": message,
            "retriable": retriable,
            "details": details or {},
        },
    }


def call_system_socket(socket_name: str, method: str, params: dict | None = None,
                       timeout: float = 10.0) -> dict | None:
    """Best-effort JSON-RPC call to a system service socket.

    Returns the result dict, or None when aether_core / the socket is not
    available. Callers must handle None honestly instead of inventing data.
    """
    try:
        from aether_core.ipc import call  # type: ignore
    except Exception:
        return None
    from pathlib import Path as _Path

    sock = _Path("/run/aether") / f"{socket_name}.sock"
    if not sock.exists():
        return None
    try:
        return call(sock, method, params or {}, timeout=timeout)
    except Exception:
        return None
