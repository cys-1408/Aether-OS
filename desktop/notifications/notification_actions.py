"""Notification action plumbing: buttons -> real method calls."""
from __future__ import annotations


def action_map(nid: str) -> dict:
    return {
        "open-settings": ("aether-settings", []),
        "retry": ("aetherctl", ["toast", "retrying…"]),
        "dismiss": ("notifications", "Notify.close"),
    }
