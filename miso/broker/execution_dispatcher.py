"""Dispatch by provider: desktop / system:<svc> / agent-local executors."""
from __future__ import annotations

import importlib

from aether_core.ipc import call
from aether_core import paths
from aether_core.errors import IpcError

# registered agent-local executors
EXECUTORS = {
    "search_files": ("files", "search_files"),
    "show_file_metadata": ("files", "show_file_metadata"),
    "open_file": ("files", "open_file"),
    "create_folder": ("files", "create_folder"),
    "copy_file": ("files", "copy_file"),
    "move_file": ("files", "move_file"),
    "rename_file": ("files", "rename_file"),
    "move_to_trash": ("files", "move_to_trash"),
    "restore_from_trash": ("files", "restore_from_trash"),
    "index_file": ("files", "index_file"),
    "create_document": ("writer", "create_document"),
    "open_document": ("writer", "open_document"),
    "save_draft": ("writer", "save_draft"),
    "summarize_selected_document": ("writer", "summarize_selected_document"),
    "read_setting": ("settings", "read_setting"),
    "change_setting": ("settings", "change_setting"),
    "recommend_model": ("models", "recommend_model"),
    "get_cpu_memory_status": ("system", "get_cpu_memory_status"),
}

SHELL_METHODS = {
    "list_apps": "Shell.list_apps", "open_app": "Shell.open_app", "close_app": "Shell.close_app",
    "focus_app": "Shell.focus_app", "create_workspace": "Shell.create_workspace",
    "list_windows": "Shell.list_windows", "arrange_windows": "Shell.arrange_windows",
    "tile_windows": "Shell.tile_windows", "minimize_window": "Shell.minimize_window",
    "restore_window": "Shell.restore_window",
    "start_focus_session": "Shell.start_focus", "pause_focus_session": "Shell.pause_focus",
    "end_focus_session": "Shell.end_focus", "start_break": "Shell.start_focus",
}

SYSTEM_ROUTES = {
    "get_cpu_memory_status": ("hardware-probe", "Hardware.summary"),
    "get_storage_status": ("hardware-probe", "Hardware.storage"),
    "get_network_status": ("network", "Network.status"),
    "get_battery_status": ("hardware-probe", "Hardware.power"),
    "get_service_status": ("health", "Health.services"),
    "read_selected_logs": ("logs", "Logs.query"),
    "get_runtime_status": ("runtime", "Runtime.status"),
    "list_models": ("runtime", "Runtime.models_list"),
    "recommend_model": ("runtime", "Runtime.models_recommend"),
    "start_download": ("runtime", "Runtime.download_start"),
    "cancel_download": ("runtime", "Runtime.download_cancel"),
    "switch_model": ("runtime", "Runtime.warmup"),
    "index_file": ("intentfs", "IntentFS.reindex"),
    "save_workspace": ("workspace", "Workspace.save"),
    "preview_workspace_restore": ("workspace", "Workspace.preview_restore"),
    "restore_workspace": ("workspace", "Workspace.restore"),
}


def dispatch(cap: dict, params: dict, peer_uid: int) -> dict:
    cid = cap["id"]
    provider = cap.get("provider", "")
    if provider == "desktop" and cid in SHELL_METHODS:
        result = call(paths.user_socket("shell"), SHELL_METHODS[cid], params, timeout=cap.get("timeout_s", 15))
        return result or {"ok": True}
    if provider.startswith("system:") and cid in SYSTEM_ROUTES:
        svc, method = SYSTEM_ROUTES[cid]
        result = call(paths.system_socket(svc), method, params, timeout=cap.get("timeout_s", 15))
        return result or {"ok": True}
    if cid in EXECUTORS:
        group, fn = EXECUTORS[cid]
        module = importlib.import_module(f"capabilities.{group}.{fn}")
        return module.run(params, peer_uid=peer_uid)
    raise IpcError("E_DISPATCH", f"no route for capability {cid} (provider {provider})")
