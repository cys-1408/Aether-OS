"""Session environment setup (user dirs, env, locale)."""
from __future__ import annotations

import os
import subprocess


def prepare() -> dict:
    steps = {}
    try:
        subprocess.run(["xdg-user-dirs-update"], timeout=10, capture_output=True)
        steps["xdg_user_dirs"] = "ok"
    except (FileNotFoundError, subprocess.TimeoutExpired):
        steps["xdg_user_dirs"] = "skipped (tool absent)"
    os.environ.setdefault("QT_QPA_PLATFORMTHEME", "")
    os.environ.setdefault("MOZ_ENABLE_WAYLAND", "1")
    steps["wayland_env"] = "set"
    return steps
