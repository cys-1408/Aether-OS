"""Battery + thermal facts (honest when absent)."""
from __future__ import annotations

from pathlib import Path


def battery() -> dict:
    for ps in Path("/sys/class/power_supply").glob("*"):
        try:
            if (ps / "type").read_text().strip() == "Battery":
                return {"capacity_pct": int((ps / "capacity").read_text().strip()),
                        "status": (ps / "status").read_text().strip()}
        except (OSError, ValueError):
            continue
    return {"present": False, "note": "no battery on this machine"}


def thermal() -> list[dict]:
    zones = []
    for z in Path("/sys/class/thermal").glob("thermal_zone*"):
        try:
            zones.append({"zone": z.name, "temp_c": int((z / "temp").read_text().strip()) / 1000})
        except (OSError, ValueError):
            continue
    return zones
