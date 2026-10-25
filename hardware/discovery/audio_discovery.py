"""Audio discovery."""
from __future__ import annotations

import shutil
import subprocess
from pathlib import Path


def discover() -> dict:
    cards = []
    try:
        for line in Path("/proc/asound/cards").read_text().splitlines():
            parts = line.strip().split(None, 1)
            if parts and parts[0].isdigit() and len(parts) > 1:
                cards.append(parts[1].strip(" []"))
    except OSError:
        pass
    server = "PipeWire" if shutil.which("wpctl") else ("PulseAudio" if shutil.which("pactl") else None)
    return {"cards": cards, "server": server}
