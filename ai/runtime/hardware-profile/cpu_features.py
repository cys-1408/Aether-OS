"""CPU instruction-set features (measured)."""
from __future__ import annotations

from pathlib import Path


def cpu_flags() -> list[str]:
    try:
        for line in Path("/proc/cpuinfo").read_text().splitlines():
            if line.startswith("flags"):
                return line.split(":", 1)[1].split()
    except OSError:
        pass
    return []


def has_avx2() -> bool:
    return "avx2" in cpu_flags()
