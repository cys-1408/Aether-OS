"""Session lock via swaylock with auto-lock policy."""
from __future__ import annotations

import shutil
import subprocess


def lock() -> dict:
    if not shutil.which("swaylock"):
        return {"locked": False, "reason": "swaylock not installed"}
    subprocess.Popen(["swaylock", "-f"])
    return {"locked": True, "locker": "swaylock"}


def auto_lock_minutes() -> int:
    from aether_core.config import load_yaml
    user = load_yaml(__import__("pathlib").Path.home() / ".config/aether/lock.yaml")
    return int(user.get("auto_lock_minutes", 15))
