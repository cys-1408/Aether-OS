"""Session history persisted in user state."""
from __future__ import annotations

import json
from pathlib import Path

from aether_core import paths

FILE = paths.USER_STATE_DIR / "calculator-history.json"


class HistoryModel:
    def __init__(self):
        self.items: list[str] = []
        if FILE.exists():
            try:
                self.items = json.loads(FILE.read_text())
            except json.JSONDecodeError:
                self.items = []

    def add(self, line: str) -> None:
        self.items.append(line)
        self.items = self.items[-50:]
        paths.USER_STATE_DIR.mkdir(parents=True, exist_ok=True)
        FILE.write_text(json.dumps(self.items))

    def recent(self, n: int = 3) -> list[str]:
        return self.items[-n:]
