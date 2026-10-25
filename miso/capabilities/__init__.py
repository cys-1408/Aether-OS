"""Real capability implementations, one module per capability id.

Every module exposes ``execute(params: dict, ctx: dict) -> dict`` where
``ctx`` carries at least ``{"uid", "request_id", "task_id", "undo_of",
"confirmation_id", "home"}``. Modules validate params defensively, perform
real work (service IPC, argv-only subprocess, filesystem), and return
verifiable facts. They never spawn a shell and never fabricate success.
"""

from __future__ import annotations

from aether_core.errors import AetherError

GROUP_DIRS = {
    "app": "miso.capabilities.apps",
    "window": "miso.capabilities.windows",
    "files": "miso.capabilities.files",
    "writer": "miso.capabilities.writer",
    "focus": "miso.capabilities.focus",
    "system-status": "miso.capabilities.system",
    "model": "miso.capabilities.models",
    "workspace": "miso.capabilities.workspaces",
    "settings": "miso.capabilities.settings",
}


def resolve_module_name(capability_id: str, group: str) -> str:
    """Dotted module path of the implementation for one capability id."""
    package = GROUP_DIRS.get(group)
    if package is None:
        raise AetherError("unknown_group", f"no capability package for group {group!r}")
    return f"{package}.{capability_id}"
