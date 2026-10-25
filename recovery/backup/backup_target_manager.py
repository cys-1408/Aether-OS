"""Attach/detach backup target media."""
from __future__ import annotations

import subprocess


def mount_target(device: str, mount: str) -> dict:
    subprocess.run(["mkdir", "-p", mount], check=False)
    out = subprocess.run(["mount", device, mount], capture_output=True, text=True, timeout=60)
    return {"mounted": out.returncode == 0, "mount": mount}
