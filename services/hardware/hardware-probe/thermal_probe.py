"""Thermal zones from /sys/class/thermal (empty list when unsupported)."""
from __future__ import annotations

from pathlib import Path


def thermal_facts() -> list[dict]:
    out = []
    for zone in sorted(Path("/sys/class/thermal").glob("thermal_zone*")):
        temp = None
        try:
            temp = int((zone / "temp").read_text().strip()) / 1000.0
        except (OSError, ValueError):
            pass
        ztype = None
        try:
            ztype = (zone / "type").read_text().strip()
        except OSError:
            pass
        out.append({"zone": zone.name, "type": ztype, "temp_c": temp})
    return out
