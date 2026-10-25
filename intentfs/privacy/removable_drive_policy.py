"""Removable drives: index only after per-device consent (ask by default)."""
from __future__ import annotations

import json
from pathlib import Path

from aether_core import paths

CONSENT = paths.USER_STATE_DIR / "removable-consent.json"


def consent_for(device: str) -> str:
    if CONSENT.exists():
        try:
            return json.loads(CONSENT.read_text()).get(device, "ask")
        except json.JSONDecodeError:
            pass
    return "ask"
