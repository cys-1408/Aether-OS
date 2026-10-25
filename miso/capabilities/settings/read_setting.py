"""read_setting: registered keys only."""
from __future__ import annotations

from aether_core.config import load_yaml

REGISTERED = ("focus_minutes", "reduced_motion", "distraction_protection",
              "text_only_mode", "mic_mute", "volume")


def run(params: dict, peer_uid: int = 0) -> dict:
    key = str(params.get("key", ""))
    if key not in REGISTERED:
        from aether_core.errors import IpcError
        raise IpcError("E_NOT_REGISTERED", f"setting {key!r} not registered")
    cfg = load_yaml(Path(__file__).resolve().parents[3] / "rootfs/etc/aether/miso.yaml") if False else {}
    user = load_yaml(Path.home() / ".config/aether/user.yaml")
    return {"key": key, "value": (user or {}).get("shell", {}).get(key)}
