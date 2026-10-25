"""Real audio facts: ALSA cards + PipeWire reachability."""
from __future__ import annotations

import shutil
import subprocess
from pathlib import Path


def audio_facts() -> dict:
    cards = []
    try:
        text = Path("/proc/asound/cards").read_text()
        for line in text.splitlines():
            parts = line.strip().split(None, 1)
            if parts and parts[0].isdigit() and len(parts) > 1:
                cards.append(parts[1].strip(" []"))
    except OSError:
        pass
    server = None
    if shutil.which("wpctl"):
        try:
            out = subprocess.run(["wpctl", "status"], capture_output=True, text=True, timeout=5)
            server = "PipeWire" if out.returncode == 0 else None
        except subprocess.TimeoutExpired:
            server = None
    elif shutil.which("pactl"):
        server = "PulseAudio-compatible"
    return {"cards": cards, "server": server}
