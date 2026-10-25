"""Safe model memory budget from availability + reserves."""
from __future__ import annotations

from pathlib import Path


def available_mb() -> int:
    try:
        with open("/proc/meminfo") as fh:
            for line in fh:
                if line.startswith("MemAvailable:"):
                    return int(line.split()[1]) // 1024
    except (OSError, ValueError):
        pass
    return 0


def budget_mb(os_reserve: int = 1024, desktop_reserve: int = 1024) -> int:
    return max(0, available_mb() - os_reserve - desktop_reserve)
