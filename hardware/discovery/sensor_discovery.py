"""Hardware sensor discovery (hwmon)."""
from __future__ import annotations

from pathlib import Path


def discover() -> list[dict]:
    out = []
    for chip in sorted(Path("/sys/class/hwmon").glob("hwmon*")):
        name = chip / "name"
        try:
            out.append({"chip": chip.name, "name": name.read_text().strip()})
        except OSError:
            continue
    return out
