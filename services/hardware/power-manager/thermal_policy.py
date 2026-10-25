"""Thermal policy guidance from real zone state."""
from __future__ import annotations

from pathlib import Path


def guidance() -> dict:
    zones = []
    hottest = None
    for zone in sorted(Path("/sys/class/thermal").glob("thermal_zone*")):
        try:
            temp = int((zone / "temp").read_text().strip()) / 1000.0
        except (OSError, ValueError):
            continue
        zones.append(temp)
        hottest = max(hottest or 0, temp)
    if hottest is None:
        state = "unknown"
    elif hottest >= 90:
        state = "critical"
    elif hottest >= 75:
        state = "hot"
    else:
        state = "normal"
    return {"hottest_c": hottest, "state": state,
            "inference_policy": {"critical": "pause", "hot": "throttle", "normal": "run"}.get(state, "run")}
