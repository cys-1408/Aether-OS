"""Suspend/resume via systemd-logind; reports real support."""
from __future__ import annotations

import subprocess
from pathlib import Path


def supported_states() -> list[str]:
    try:
        return Path("/sys/power/state").read_text().split()
    except OSError:
        return []


def suspend() -> dict:
    if "mem" not in supported_states() and "s2idle" not in supported_states():
        return {"ok": False, "reason": "suspend not supported by firmware/kernel state"}
    try:
        subprocess.run(["systemctl", "suspend"], check=True, timeout=30)
        return {"ok": True}
    except (subprocess.TimeoutExpired, subprocess.CalledProcessError) as e:
        return {"ok": False, "reason": str(e)}
