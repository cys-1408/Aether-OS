"""Power/thermal state for the governor."""
from __future__ import annotations

from pathlib import Path


def power_state() -> dict:
    ac = None
    for ps in Path("/sys/class/power_supply").glob("*"):
        try:
            if (ps / "type").read_text().strip() == "Mains":
                ac = (ps / "online").read_text().strip() == "1"
        except OSError:
            continue
    return {"ac_online": ac}


def thermal_state() -> str:
    hottest = 0.0
    for z in Path("/sys/class/thermal").glob("thermal_zone*"):
        try:
            hottest = max(hottest, int((z / "temp").read_text().strip()) / 1000)
        except (OSError, ValueError):
            continue
    if hottest == 0:
        return "unknown"
    return "critical" if hottest >= 90 else "hot" if hottest >= 75 else "normal"
