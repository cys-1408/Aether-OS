"""Printer device discovery via CUPS lpinfo."""
from __future__ import annotations

import shutil
import subprocess


def discover() -> dict:
    if not shutil.which("lpinfo"):
        return {"supported": False, "reason": "CUPS not installed"}
    out = subprocess.run(["lpinfo", "-v"], capture_output=True, text=True, timeout=20)
    return {"devices": [l.strip() for l in out.stdout.splitlines() if l.strip()]}
