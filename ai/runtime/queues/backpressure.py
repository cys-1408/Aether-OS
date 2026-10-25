"""PSI-driven backpressure: pause background work under memory pressure."""
from __future__ import annotations

from pathlib import Path

THRESHOLD = 60.0


def memory_psi_avg10() -> float | None:
    try:
        for line in Path("/proc/pressure/memory").read_text().splitlines():
            if line.startswith("some avg10="):
                return float(line.split("avg10=")[1].split()[0])
    except (OSError, ValueError):
        pass
    return None


def background_should_pause() -> dict:
    psi = memory_psi_avg10()
    if psi is None:
        return {"paused": False, "reason": "PSI unavailable"}
    return {"paused": psi > THRESHOLD, "psi": psi, "threshold": THRESHOLD}
