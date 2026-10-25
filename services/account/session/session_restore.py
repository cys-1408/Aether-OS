"""Session restore: ask the workspace service for the last saved layout."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from service_main import SystemService  # noqa: E402


def restore_last(uid: int) -> dict:
    probe = SystemService("session", "session", {})
    result = probe.call_service("workspace", "Workspace.list", {"uid": uid})
    if not result:
        return {"restored": False, "reason": "workspace service unreachable"}
    items = result.get("workspaces", [])
    if not items:
        return {"restored": False, "reason": "no saved workspaces"}
    last = items[-1]
    preview = probe.call_service("workspace", "Workspace.preview_restore", {"workspace_id": last["workspace_id"]})
    return {"restored": False, "preview_available": bool(preview),
            "workspace": last, "note": "restore requires explicit user confirmation"}
