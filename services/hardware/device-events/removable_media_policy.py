"""Removable media policy: indexing consent per drive (ask by default)."""
from __future__ import annotations

from pathlib import Path

from aether_core.config import load_yaml


def consent_for(device: str) -> dict:
    defaults = load_yaml("/etc/aether/privacy-defaults.yaml")
    policy = (defaults.get("removable_media") or {}).get("index_consent", "ask")
    user_state = Path.home() / ".local/share/aether/removable-consent.json"
    per_device = {}
    if user_state.exists():
        import json
        per_device = json.loads(user_state.read_text())
    if device in per_device:
        policy = per_device[device]
    return {"device": device, "index_consent": policy}
