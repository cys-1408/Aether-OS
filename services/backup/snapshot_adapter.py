"""System snapshots: btrfs when available — honest capability reporting."""
from __future__ import annotations

import shutil
import subprocess


def snapshot(root_mount: str = "/", name: str = "") -> dict:
    if not shutil.which("btrfs"):
        return {"supported": False, "reason": "btrfs-progs not installed"}
    fstype = subprocess.run(["findmnt", "-n", "-o", "FSTYPE", root_mount],
                            capture_output=True, text=True, timeout=5).stdout.strip()
    if fstype != "btrfs":
        return {"supported": False, "reason": f"root is {fstype or 'unknown'}, not btrfs"}
    snap_path = f"{root_mount}.snapshots/{name or 'manual-' + str(int(__import__('time').time()))}"
    out = subprocess.run(["btrfs", "subvolume", "snapshot", root_mount, snap_path],
                         capture_output=True, text=True, timeout=60)
    return {"supported": True, "ok": out.returncode == 0, "snapshot": snap_path,
            "error": None if out.returncode == 0 else out.stderr.strip()}
