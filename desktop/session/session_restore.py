"""Restore last workspace layout with explicit user approval."""
from __future__ import annotations


def preview(shell) -> dict | None:
    from aether_core.ipc import call
    from aether_core.errors import IpcError
    from aether_core import paths
    try:
        data = call(paths.system_socket("workspace"), "Workspace.list", {}, timeout=5)
        items = data.get("workspaces", [])
        if not items:
            return None
        last = items[-1]
        return call(paths.system_socket("workspace"), "Workspace.preview_restore",
                    {"workspace_id": last["workspace_id"]}, timeout=10)
    except IpcError:
        return None


def restore(shell, workspace_id: str) -> dict:
    from aether_core.ipc import call
    from aether_core.errors import IpcError
    from aether_core import paths
    try:
        return call(paths.system_socket("workspace"), "Workspace.restore",
                    {"workspace_id": workspace_id, "confirmed": True}, timeout=30)
    except IpcError as e:
        return {"restored": False, "reason": e.message}
