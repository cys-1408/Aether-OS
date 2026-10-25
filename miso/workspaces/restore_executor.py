"""Apply the restore AFTER explicit confirmation (preview-then-apply)."""
from __future__ import annotations

from aether_core.ipc import call
from aether_core.errors import IpcError
from aether_core import paths


def apply(doc: dict) -> dict:
    layout = doc.get("layout", {})
    opened = []
    for win in layout.get("windows", []):
        app = win.get("app_id")
        if app:
            try:
                call(paths.user_socket("shell"), "Shell.open_app", {"app": app}, timeout=20)
                opened.append(app)
            except IpcError:
                continue
    return {"restored": True, "opened": opened, "workspace_id": doc.get("workspace_id")}
