"""Battery-aware background-work guidance (facts only)."""
from __future__ import annotations

from pathlib import Path


def guidance() -> dict:
    ac = None
    battery = None
    for ps in sorted(Path("/sys/class/power_supply").glob("*")):
        try:
            ptype = (ps / "type").read_text().strip()
        except OSError:
            continue
        if ptype == "Mains":
            try:
                ac = (ps / "online").read_text().strip() == "1"
            except OSError:
                pass
        elif ptype == "Battery" and battery is None:
            try:
                battery = int((ps / "capacity").read_text().strip())
            except (OSError, ValueError):
                pass
    if ac is False and battery is not None and battery < 20:
        background = "pause"
    elif ac is False:
        background = "throttle"
    else:
        background = "run"
    return {"ac_online": ac, "battery_pct": battery, "background_work": background}
