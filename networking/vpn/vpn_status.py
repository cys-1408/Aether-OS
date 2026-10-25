"""VPN status entry point for AetherOS diagnostics.

Thin public wrapper around :mod:`vpn_provider_interface` so callers only need
one import; adds timestamping and honest error reporting.
"""
from __future__ import annotations

import datetime as _dt
import sys
from pathlib import Path

_PKG_DIR = Path(__file__).resolve().parent
if str(_PKG_DIR) not in sys.path:
    sys.path.insert(0, str(_PKG_DIR))
_CM_DIR = _PKG_DIR.parent / "connection-manager"
if str(_CM_DIR) not in sys.path:
    sys.path.insert(0, str(_CM_DIR))

import _nm  # noqa: E402  (shared connection-manager helper module)
from vpn_provider_interface import vpn_status  # noqa: E402


def status(timeout_s: float = 15.0) -> dict:
    """Return the NetworkManager VPN status summary with a timestamp."""
    try:
        result = vpn_status(timeout_s=timeout_s)
    except _nm.ToolNotFound as exc:
        result = {"supported": False, "reason": str(exc), "active": [], "configured": []}
    result["checked_at"] = _dt.datetime.now(_dt.timezone.utc).isoformat()
    return result


def active_tunnels(timeout_s: float = 15.0) -> list[str]:
    """Return just the names of currently active tunnels (empty when none)."""
    result = status(timeout_s=timeout_s)
    return list(result.get("active", []))
