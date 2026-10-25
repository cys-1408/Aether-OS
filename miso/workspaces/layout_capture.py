"""Capture the current layout from the shell (real sway state)."""
from __future__ import annotations

from aether_core.ipc import call
from aether_core.errors import IpcError
from aether_core import paths


def capture_current() -> dict:
    try:
        windows = call(paths.user_socket("shell"), "Shell.list_windows", {}, timeout=8)
        workspaces = call(paths.user_socket("shell"), "Shell.list_workspaces", {}, timeout=5)
        return {"windows": (windows or {}).get("windows", []),
                "workspaces": (workspaces or {}).get("workspaces", [])}
    except IpcError:
        return {"windows": [], "workspaces": [], "note": "session unreachable; layout empty"}
