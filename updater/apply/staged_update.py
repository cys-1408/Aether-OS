"""Staged update activation gate: downloads first, activation only after a
verified stage and explicit confirmation."""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from staging import stage  # noqa: E402
from apply import apply  # noqa: E402
from planning.update_plan import plan  # noqa: E402


def stage_update() -> dict:
    """Download-only stage; safe to run unattended (pacman -Sw)."""
    p = plan()
    if p.get("blocked"):
        return {"staged": False, "reason": p["blocked"], "plan": p}
    res = stage()
    return {"staged": res.get("staged", False), "detail": res.get("detail"),
            "plan": p}


def activate(confirmed: bool, *, digests_verified: bool = False) -> dict:
    """Activate a staged update. Requires explicit confirmation AND digest
    verification from updater/verification/package_digest."""
    if not confirmed:
        return {"activated": False, "reason": "user confirmation required"}
    if not digests_verified:
        return {"activated": False,
                "reason": "package digests not verified; refusing to apply"}
    return apply(confirmed=True)
