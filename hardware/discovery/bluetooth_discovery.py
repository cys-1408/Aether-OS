"""Bluetooth discovery (honest when stack absent)."""
from __future__ import annotations

import shutil
import subprocess


def discover() -> dict:
    if not shutil.which("bluetoothctl"):
        return {"supported": False, "reason": "bluetoothctl not installed (bluez optional)"}
    try:
        out = subprocess.run(["bluetoothctl", "devices"], capture_output=True, text=True, timeout=10)
        return {"supported": True, "devices": out.stdout.splitlines()}
    except subprocess.TimeoutExpired:
        return {"supported": True, "devices": [], "reason": "bluetoothctl timeout"}
