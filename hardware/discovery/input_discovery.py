"""Input device discovery."""
from __future__ import annotations

from pathlib import Path


def discover() -> list[dict]:
    out = []
    try:
        for block in Path("/proc/bus/input/devices").read_text().split("\n\n"):
            lines = block.splitlines()
            name = next((l.split("=", 1)[1].strip('"') for l in lines if l.startswith("N:")), None)
            handlers = next((l.split("=", 1)[1].strip() for l in lines if l.startswith("H:")), None)
            if name:
                out.append({"name": name, "handlers": handlers})
    except OSError:
        pass
    return out
