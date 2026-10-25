"""Memory discovery (real sources)."""
from __future__ import annotations

from pathlib import Path


def discover() -> dict:
    total = avail = 0
    try:
        with open("/proc/meminfo") as fh:
            for line in fh:
                if line.startswith("MemTotal:"):
                    total = int(line.split()[1]) // 1024
                elif line.startswith("MemAvailable:"):
                    avail = int(line.split()[1]) // 1024
    except (OSError, ValueError):
        pass
    return {"total_mb": total, "available_mb": avail}
