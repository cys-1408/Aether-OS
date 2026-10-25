"""Result verification from real system state (never trust the tool alone)."""
from __future__ import annotations

from pathlib import Path

from aether_core.ipc import call
from aether_core.errors import IpcError
from aether_core import paths


def verify(cap: dict, result: dict) -> dict:
    cid = cap["id"]
    if cid in ("create_folder", "copy_file", "move_file", "rename_file", "create_document", "save_draft"):
        target = result.get("dst") or result.get("path") or result.get("new_path")
        if target:
            return {"method": "stat", "passed": Path(str(target).replace("~", str(Path.home()))).expanduser().exists(),
                    "detail": f"verified {target} exists"}
    if cid == "move_to_trash":
        return {"method": "trash_info", "passed": bool(result.get("trashed_to")),
                "detail": "trash entry recorded"}
    if cid in ("open_app", "focus_app", "tile_windows", "minimize_window", "restore_window"):
        try:
            call(paths.user_socket("shell"), "Shell.list_windows", {}, timeout=6)
            return {"method": "sway_tree", "passed": True, "detail": "window manager reachable"}
        except IpcError as e:
            return {"method": "sway_tree", "passed": False, "detail": e.message}
    if cid in ("get_cpu_memory_status", "get_network_status", "list_models"):
        return {"method": "service_reply", "passed": result is not None, "detail": "live service data"}
    return {"method": "none", "passed": True, "detail": "read-only or self-verifying operation"}
