"""AT-SPI bridge init (pyatspi guard-import; honest unavailability)."""
from __future__ import annotations

import os


def initialize() -> dict:
    os.environ.setdefault("GTK_MODULES", "gail:atk-bridge")
    try:
        import pyatspi  # noqa: F401
        return {"screen_reader": "AT-SPI available"}
    except ImportError:
        return {"screen_reader": "AT-SPI (pyatspi) not installed — keyboard navigation still fully supported"}


def orca_running() -> bool:
    try:
        import subprocess
        out = subprocess.run(["pgrep", "-x", "orca"], capture_output=True, text=True, timeout=3)
        return out.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False
