"""World clocks via stdlib zoneinfo (real offsets)."""
from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo

ZONES = ["Asia/Kolkata", "Europe/London", "America/New_York", "Asia/Tokyo", "UTC"]


def world_clocks() -> str:
    parts = []
    for zone in ZONES:
        try:
            dt = datetime.now(ZoneInfo(zone))
            parts.append(f"{zone.split('/')[-1]} {dt.strftime('%H:%M')}")
        except Exception:
            continue
    return "   ·   ".join(parts)
