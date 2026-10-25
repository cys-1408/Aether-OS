"""Block device discovery via lsblk -J."""
from __future__ import annotations

import json
import subprocess


def discover() -> dict:
    try:
        out = subprocess.run(
            ["lsblk", "-J", "-b", "-o", "NAME,SIZE,TYPE,FSTYPE,MOUNTPOINT,RM,MODEL"],
            capture_output=True, text=True, timeout=5)
        if out.returncode == 0:
            return {"blockdevices": json.loads(out.stdout).get("blockdevices", [])}
        return {"blockdevices": [], "error": out.stderr.strip()}
    except (FileNotFoundError, subprocess.TimeoutExpired, json.JSONDecodeError) as e:
        return {"blockdevices": [], "error": str(e)}
