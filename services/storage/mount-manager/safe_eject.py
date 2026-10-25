"""Safe eject: unmount + power-off with truthful busy reporting."""
from __future__ import annotations

import re
import subprocess


def _busy_processes(device: str) -> list[str]:
    try:
        out = subprocess.run(["fuser", "-vm", device], capture_output=True, text=True, timeout=5)
        return [ln.strip() for ln in out.stdout.splitlines() if ln.strip()]
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return []


def eject(device: str) -> dict:
    import mount_service
    un = mount_service.unmount(device)
    if not un.get("ok"):
        return {"ok": False, "stage": "unmount", "error": un.get("error"),
                "busy_processes": _busy_processes(device)}
    try:
        out = subprocess.run(["udisksctl", "power-off", "-b", device],
                             capture_output=True, text=True, timeout=15)
        return {"ok": out.returncode == 0, "stage": "power-off",
                "error": None if out.returncode == 0 else out.stderr.strip()}
    except FileNotFoundError:
        return {"ok": True, "stage": "unmount", "note": "power-off unavailable (udisksctl missing)"}
