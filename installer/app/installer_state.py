"""Installer state: persisted to /run/aether/installer-state.json (resume)."""
from __future__ import annotations

import json
import time
from pathlib import Path

from aether_core.config import atomic_write_json

STATE = Path("/run/aether/installer-state.json")


class InstallerState:
    def __init__(self):
        self.data = {"version": 1, "completed_steps": [], "choices": {}, "started_at": None}
        self.load()

    def load(self) -> None:
        if STATE.exists():
            try:
                self.data = json.loads(STATE.read_text())
            except json.JSONDecodeError:
                pass
        self.data.setdefault("started_at", time.strftime("%Y-%m-%dT%H:%M:%S%z"))

    def save(self) -> None:
        atomic_write_json(STATE, self.data, mode=0o600)

    def commit(self, step: str, choices: dict | None = None) -> None:
        if step not in self.data["completed_steps"]:
            self.data["completed_steps"].append(step)
        if choices:
            self.data["choices"].update(choices)
        self.save()

    def done(self, step: str) -> bool:
        return step in self.data["completed_steps"]

    def choices_merged(self) -> dict:
        return dict(self.data["choices"])
