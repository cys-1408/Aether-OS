"""Icon layout persistence (user-approved positions)."""
from __future__ import annotations

import json
from pathlib import Path

from aether_core import paths

LAYOUT_FILE = paths.USER_CONFIG_DIR / "desktop-icons.json"


def save_layout(entries: list[dict]) -> dict:
    paths.USER_CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    LAYOUT_FILE.write_text(json.dumps(entries, indent=2))
    return {"saved": len(entries)}


def load_layout() -> list[dict]:
    if LAYOUT_FILE.exists():
        return json.loads(LAYOUT_FILE.read_text())
    return []
