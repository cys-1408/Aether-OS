"""Category policy from privacy defaults + user overrides."""
from __future__ import annotations

from aether_core.config import load_yaml

SYSTEM_CATEGORIES = ["device", "service_failed", "service_recovered", "updates",
                     "reminder", "backup", "download", "indexing", "focus"]


def category_enabled(category: str, uid: int | None = None) -> dict:
    if category not in SYSTEM_CATEGORIES:
        return {"enabled": True, "reason": "uncategorized pass-through (rate limited)"}
    # System categories are on; user-specific opt-outs live in miso.yaml presence section
    miso = load_yaml("/etc/aether/miso.yaml")
    presence = (miso.get("presence") or {}).get("categories", {})
    if category in presence:
        return {"enabled": bool(presence[category])}
    return {"enabled": True}
