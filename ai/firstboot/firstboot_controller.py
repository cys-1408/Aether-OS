"""AI-setup controller used by the first-boot wizard (resumable)."""
from __future__ import annotations

import json
import time
from pathlib import Path

from aether_core.config import atomic_write_json
from aether_core import paths

STATE = paths.SYSTEM_STATE_DIR / "firstboot-ai-state.json"


def load_state() -> dict:
    if STATE.exists():
        return json.loads(STATE.read_text())
    return {"pages": [], "choices": {}}


def commit_page(page: str, choices: dict) -> dict:
    state = load_state()
    if page not in state["pages"]:
        state["pages"].append(page)
    state["choices"].update(choices)
    state["updated_at"] = time.strftime("%Y-%m-%dT%H:%M:%S%z")
    atomic_write_json(STATE, state)
    return state


def is_complete() -> bool:
    return "optional_ai" in load_state().get("pages", [])
