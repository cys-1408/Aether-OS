"""Printer discovery (CUPS when present)."""
from __future__ import annotations

import shutil
import subprocess


def discover() -> dict:
    if not shutil.which("lpinfo"):
        return {"supported": False, "reason": "CUPS not installed"}
    out = subprocess.run(["lpinfo", "-v"], capture_output=True, text=True, timeout=20)
    return {"supported": True, "devices": out.stdout.splitlines()}
