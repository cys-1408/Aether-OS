"""Recent apps list persisted in user config."""
from __future__ import annotations

import json
from pathlib import Path

from aether_core import paths

FILE = paths.USER_CONFIG_DIR / "recent-apps.json"


def remember(name: str) -> None:
    recent = load()
    if name in recent:
        recent.remove(name)
    recent.insert(0, name)
    paths.USER_CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    FILE.write_text(json.dumps(recent[:10]))


def load() -> list[str]:
    if FILE.exists():
        return json.loads(FILE.read_text())
    return []
