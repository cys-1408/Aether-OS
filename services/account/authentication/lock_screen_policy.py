"""Lock screen settings (consumed by the desktop session_lock)."""
from __future__ import annotations

from aether_core.config import load_yaml


def effective_policy() -> dict:
    defaults = {"auto_lock_minutes": 15, "locker": "swaylock", "enabled": True}
    user = load_yaml("~/.config/aether/lock.yaml".replace("~", str(__import__("pathlib").Path.home())))
    defaults.update(user or {})
    return defaults
