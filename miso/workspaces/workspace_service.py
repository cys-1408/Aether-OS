"""Living Workspaces: capture → store → preview → confirm → restore."""
from __future__ import annotations

import json
import time
import uuid
from pathlib import Path

from aether_core import paths
from aether_core.errors import IpcError

STORE = paths.SYSTEM_STATE_DIR / "workspaces"


class WorkspaceService:
    def save(self, uid: int, name: str, layout: dict) -> dict:
        wid = f"ws-{uuid.uuid4().hex[:10]}"
        STORE.mkdir(parents=True, exist_ok=True)
        (STORE / f"{uid}").mkdir(exist_ok=True)
        doc = {"workspace_id": wid, "name": name or "workspace", "version": 1,
               "created_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
               "updated_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
               "layout": layout, "uid": uid}
        (STORE / f"{uid}" / f"{wid}.json").write_text(json.dumps(doc, indent=2))
        return {"workspace_id": wid, "saved": True}

    def list(self, uid: int) -> dict:
        out = []
        base = STORE / f"{uid}"
        if base.exists():
            for f in sorted(base.glob("*.json")):
                doc = json.loads(f.read_text())
                out.append({"workspace_id": doc["workspace_id"], "name": doc["name"],
                            "updated_at": doc["updated_at"]})
        return {"workspaces": out}

    def preview_restore(self, uid: int, workspace_id: str) -> dict:
        doc = self._load(uid, workspace_id)
        from restore_preview import build_preview
        return {"preview": build_preview(doc)}

    def restore(self, uid: int, workspace_id: str, confirmed: bool) -> dict:
        if not confirmed:
            raise IpcError("E_CONFIRMATION", "restore requires explicit user confirmation of the preview")
        doc = self._load(uid, workspace_id)
        from restore_executor import apply
        return apply(doc)

    def delete(self, uid: int, workspace_id: str) -> dict:
        p = STORE / f"{uid}" / f"{workspace_id}.json"
        if p.exists():
            p.unlink()
            return {"deleted": workspace_id}
        raise IpcError("E_NOT_FOUND", workspace_id)

    def _load(self, uid: int, workspace_id: str) -> dict:
        p = STORE / f"{uid}" / f"{workspace_id}.json"
        if not p.exists():
            raise IpcError("E_NOT_FOUND", f"workspace {workspace_id} not found")
        return json.loads(p.read_text())
