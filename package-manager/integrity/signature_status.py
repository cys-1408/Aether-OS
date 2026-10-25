"""Signature status from pacman-key."""
from __future__ import annotations

import subprocess


def status() -> dict:
    try:
        out = subprocess.run(["pacman-key", "--list-keys"], capture_output=True, text=True, timeout=20)
        keys = len([l for l in out.stdout.splitlines() if l.startswith("pub")])
        return {"keys": keys, "ok": out.returncode == 0}
    except FileNotFoundError:
        return {"keys": 0, "ok": False, "reason": "pacman-key not installed"}
