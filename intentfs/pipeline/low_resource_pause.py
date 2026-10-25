"""Low-resource pause hooks (PSI + battery)."""
from __future__ import annotations

from pathlib import Path


def should_pause(psi_threshold: float = 60.0, pause_on_battery: bool = True) -> dict:
    psi = None
    try:
        for line in Path("/proc/pressure/memory").read_text().splitlines():
            if line.startswith("some avg10="):
                psi = float(line.split("avg10=")[1].split()[0])
    except (OSError, ValueError):
        pass
    battery = False
    for ps in Path("/sys/class/power_supply").glob("*"):
        try:
            if (ps / "type").read_text().strip() == "Mains" and (ps / "online").read_text().strip() == "0":
                battery = True
        except OSError:
            continue
    paused = (psi is not None and psi > psi_threshold) or (battery and pause_on_battery)
    return {"paused": paused, "psi": psi, "on_battery": battery}
