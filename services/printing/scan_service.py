"""Scanner surface via SANE (scanimage) — optional, honest."""
from __future__ import annotations

import shutil
import subprocess


def devices() -> dict:
    if not shutil.which("scanimage"):
        return {"supported": False, "reason": "SANE (scanimage) not installed"}
    out = subprocess.run(["scanimage", "-L"], capture_output=True, text=True, timeout=15)
    found = [ln.strip() for ln in out.stdout.splitlines() if ln.strip().startswith("device")]
    return {"supported": True, "devices": found}


def scan_to(path: str, device: str | None = None) -> dict:
    if not shutil.which("scanimage"):
        return {"ok": False, "reason": "SANE not installed"}
    argv = ["scanimage", "--format=png", "-o", path]
    if device:
        argv += ["-d", device]
    out = subprocess.run(argv, capture_output=True, text=True, timeout=120)
    return {"ok": out.returncode == 0, "file": path if out.returncode == 0 else None,
            "error": None if out.returncode == 0 else out.stderr.strip()[-400:]}
