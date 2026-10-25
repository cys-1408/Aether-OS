"""Schedule contract: aether-backup-reminder.timer + last-run state."""
from __future__ import annotations

import json
from pathlib import Path

from aether_core import paths

STATE = paths.USER_STATE_DIR / "backup-state.json"


def schedule_state() -> dict:
    st = json.loads(STATE.read_text()) if STATE.exists() else {}
    return {"timer": "aether-backup-reminder.timer (weekly)", "last_run": st.get("last_run"),
            "verified": st.get("verified", False)}
