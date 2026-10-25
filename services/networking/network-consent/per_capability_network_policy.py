"""Per-capability network egress policy — deny by default for AI caps."""
from __future__ import annotations

import json
import time
from pathlib import Path

from aether_core.config import load_yaml, atomic_write_json

STATE = Path("/var/lib/aether/consent.json")
USER_STATE = Path.home() / ".local/share/aether/consent-user.json"

AI_CAPABILITIES = {"start_download", "summarize_selected_document", "local_code_assist", "read_selected_logs"}


def check(capability_id: str, data_class: str = "personal") -> dict:
    defaults = load_yaml("/etc/aether/privacy-defaults.yaml")
    ai_default = (defaults.get("network") or {}).get("ai_capabilities", "denied-by-default")
    store = _store()
    if capability_id in store:
        return {"capability_id": capability_id, "decision": store[capability_id]["decision"],
                "granted_at": store[capability_id].get("granted_at")}
    if capability_id in AI_CAPABILITIES and ai_default == "denied-by-default":
        return {"capability_id": capability_id, "decision": "prompt",
                "reason": "AI network access is denied by default; user consent required"}
    if data_class == "public":
        return {"capability_id": capability_id, "decision": "allow",
                "reason": "public/system data class"}
    return {"capability_id": capability_id, "decision": "deny",
            "reason": "personal data class requires explicit consent"}


def grant(capability_id: str) -> dict:
    store = _store()
    store[capability_id] = {"decision": "allow", "granted_at": time.strftime("%Y-%m-%dT%H:%M:%S%z")}
    _save(store)
    return {"capability_id": capability_id, "decision": "allow"}


def revoke(capability_id: str) -> dict:
    store = _store()
    store.pop(capability_id, None)
    _save(store)
    return {"capability_id": capability_id, "decision": "revoked"}


def list_all() -> dict:
    return {"grants": {k: v["decision"] for k, v in _store().items()}}


def _store() -> dict:
    for path in (USER_STATE, STATE):
        if path.exists():
            try:
                return json.loads(path.read_text())
            except json.JSONDecodeError:
                continue
    return {}


def _save(store: dict) -> None:
    target = USER_STATE if USER_STATE.parent.exists() else STATE
    atomic_write_json(target, store, mode=0o600)
