"""Storage discovery (real lsblk)."""
from __future__ import annotations

import json
import subprocess


def discover() -> list[dict]:
    try:
        out = subprocess.run(["lsblk", "-J", "-d", "-o", "NAME,SIZE,MODEL,TYPE,ROTA"],
                             capture_output=True, text=True, timeout=10)
        return json.loads(out.stdout).get("blockdevices", [])
    except (FileNotFoundError, subprocess.TimeoutExpired, json.JSONDecodeError):
        return []
