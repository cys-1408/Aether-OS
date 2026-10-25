"""Restore preview: exact diff of what WILL happen (no side effects)."""
from __future__ import annotations


def build_preview(doc: dict) -> dict:
    layout = doc.get("layout", {})
    windows = layout.get("windows", [])
    preview = {
        "will_open": [w.get("app_id") for w in windows if w.get("app_id")],
        "will_restore_geometry": len(windows),
        "workspace_switches": [w.get("name") for w in layout.get("workspaces", [])[:3]],
        "side_effects": [],
        "terminal_commands": [],
        "note": "restore never executes terminal commands or scripts",
    }
    return preview
