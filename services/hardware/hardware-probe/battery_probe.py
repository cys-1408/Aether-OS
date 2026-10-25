"""Power supply facts from /sys/class/power_supply."""
from __future__ import annotations

from pathlib import Path


def power_facts() -> dict:
    ac_online = None
    battery = None
    for ps in sorted(Path("/sys/class/power_supply").glob("*")):
        try:
            ptype = (ps / "type").read_text().strip()
        except OSError:
            continue
        if ptype == "Mains":
            try:
                val = (ps / "online").read_text().strip()
                ac_online = val == "1"
            except OSError:
                pass
        elif ptype == "Battery" and battery is None:
            cap = status = None
            try:
                cap = int((ps / "capacity").read_text().strip())
            except (OSError, ValueError):
                pass
            try:
                status = (ps / "status").read_text().strip()
            except OSError:
                pass
            battery = {"capacity_pct": cap, "status": status}
    return {"ac_online": ac_online, "battery": battery}
