"""Download-only stage into the pacman cache."""
from __future__ import annotations

import subprocess


def stage() -> dict:
    out = subprocess.run(["pacman", "-Sw", "--noconfirm"], capture_output=True, text=True, timeout=3600)
    return {"staged": out.returncode == 0, "detail": out.stdout[-200:]}
