"""Removable mount policy: honor privacy defaults (autorun never; index asks)."""
from __future__ import annotations

from pathlib import Path

from aether_core.config import load_yaml


def policy_for(device: str, removable: bool) -> dict:
    defaults = load_yaml("/etc/aether/privacy-defaults.yaml")
    consent = (defaults.get("removable_media") or {}).get("index_consent", "ask")
    return {
        "device": device,
        "removable": bool(removable),
        "autorun": False,
        "index_consent": "always" if not removable else consent,
    }
