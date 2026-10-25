"""Undo dispatch for reversible capabilities."""
from __future__ import annotations

from aether_core.ipc import call
from aether_core.errors import IpcError
from aether_core import paths

UNDO_ROUTES = {
    "move_to_trash": ("files", "restore_from_trash"),
    "start_focus_session": ("desktop", "Shell.end_focus"),
}


def rollback(capability_id: str, undo_payload: dict) -> dict:
    route = UNDO_ROUTES.get(capability_id)
    if not route:
        return {"undone": False, "reason": "no undo route for this capability"}
    kind, target = route
    sock = paths.user_socket("shell") if kind == "desktop" else paths.user_socket("trash")
    try:
        result = call(sock, target, undo_payload, timeout=30)
        return {"undone": True, "result": result}
    except IpcError as e:
        return {"undone": False, "reason": e.message}
