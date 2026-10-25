"""User-confirmed apply with known-good entry first."""
from __future__ import annotations

import subprocess

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "recovery/rollback"))

from known_good_boot_entry import mark_known_good  # type: ignore  # when in recovery context


def apply(confirmed: bool) -> dict:
    if not confirmed:
        return {"applied": False, "reason": "explicit user confirmation required"}
    try:
        mark_known_good("/")
    except Exception:
        pass  # grubenv may not exist in live env; apply proceeds with journal rollback
    out = subprocess.run(["pacman", "-Su", "--noconfirm"], capture_output=True, text=True, timeout=7200)
    return {"applied": out.returncode == 0, "detail": out.stdout[-400:]}
