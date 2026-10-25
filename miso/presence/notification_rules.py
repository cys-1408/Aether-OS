"""Opt-in category rules (defaults from miso.yaml presence section)."""
from __future__ import annotations

from aether_core.config import load_yaml


class NotificationRules:
    def __init__(self):
        cfg = load_yaml("/etc/aether/miso.yaml") or {}
        self.categories = (cfg.get("presence", {}) or {}).get("categories", {})

    def allows(self, event: dict) -> bool:
        from event_classifier import classify
        cat = classify(event)
        return bool(self.categories.get(cat, cat == "download_completed"))
