"""CPU discovery (real sources)."""
from __future__ import annotations

from pathlib import Path


def discover() -> dict:
    model, flags = None, []
    try:
        for line in Path("/proc/cpuinfo").read_text().splitlines():
            if line.startswith("model name") and not model:
                model = line.split(":", 1)[1].strip()
            if line.startswith("flags") and not flags:
                flags = line.split(":", 1)[1].split()
    except OSError:
        pass
    cores = len(list(Path("/sys/devices/system/cpu").glob("cpu[0-9]*"))) if Path("/sys/devices/system/cpu").exists() else None
    return {"model": model, "flags": flags, "threads": cores}
