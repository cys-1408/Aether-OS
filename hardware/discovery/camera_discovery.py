"""Camera discovery."""
from __future__ import annotations

from pathlib import Path


def discover() -> list[dict]:
    out = []
    for v in sorted(Path("/sys/class/video4linux").glob("*")):
        name = v / "name"
        try:
            out.append({"device": v.name, "name": name.read_text().strip()})
        except OSError:
            continue
    return out
