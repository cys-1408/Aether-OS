"""Sound indicators using the synthesized system sounds."""
from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

SOUNDS = Path("/usr/share/aether/desktop/assets/sounds")


def play(name: str) -> dict:
    f = SOUNDS / f"{name}.wav"
    if not f.exists():
        return {"played": False, "reason": "sound not found"}
    player = shutil.which("pw-play") or shutil.which("paplay")
    if not player:
        return {"played": False, "reason": "no audio player"}
    subprocess.Popen([player, str(f)])
    return {"played": True}
