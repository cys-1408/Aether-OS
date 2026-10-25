"""Background throttle decisions."""
from __future__ import annotations


def throttle_level(battery_ac: bool | None, thermal: str) -> str:
    if thermal == "critical" or battery_ac is False:
        return "pause"
    if thermal == "hot":
        return "throttle"
    return "run"
