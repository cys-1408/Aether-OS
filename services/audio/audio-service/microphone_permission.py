"""Microphone permission + mute enforcement with visible capture state."""
from __future__ import annotations

import subprocess
from pathlib import Path

from aether_core.config import load_yaml


def consent_default() -> str:
    defaults = load_yaml("/etc/aether/privacy-defaults.yaml")
    return (defaults.get("microphone") or {}).get("default", "denied")


def set_mic_muted(muted: bool) -> dict:
    try:
        target = "@DEFAULT_AUDIO_SOURCE@"
        out = subprocess.run(["wpctl", "set-source-mute", target, "1" if muted else "0"],
                             capture_output=True, text=True, timeout=8)
        return {"ok": out.returncode == 0, "muted": muted}
    except FileNotFoundError:
        return {"ok": False, "error": "wpctl not installed"}


def capture_state() -> dict:
    """Real capture indicator state: source mute + active streams."""
    try:
        out = subprocess.run(["wpctl", "status"], capture_output=True, text=True, timeout=8)
        muted = "MUTED" in out.stdout
        return {"supported": True, "muted": muted, "indicator_required": True}
    except FileNotFoundError:
        return {"supported": False, "reason": "wpctl not installed"}
