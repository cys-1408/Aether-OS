"""change_setting: registered keys, previous value captured for undo."""
from __future__ import annotations

from pathlib import Path

from aether_core.config import load_yaml, atomic_write_yaml

REGISTERED = ("focus_minutes", "reduced_motion", "distraction_protection",
              "text_only_mode", "mic_mute", "volume")


def run(params: dict, peer_uid: int = 0) -> dict:
    key = str(params.get("key", ""))
    if key not in REGISTERED:
        from aether_core.errors import IpcError
        raise IpcError("E_NOT_REGISTERED", f"setting {key!r} not registered")
    conf = Path.home() / ".config/aether/user.yaml"
    user = load_yaml(conf) or {}
    shell = user.setdefault("shell", {})
    previous = shell.get(key)
    shell[key] = params.get("value")
    atomic_write_yaml(conf, user, mode=0o600)
    return {"ok": True, "key": key, "previous": previous, "new": params.get("value"),
            "_undo": {"key": key, "value": previous}}
