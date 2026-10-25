"""Snapshots: btrfs when available; tar of /etc otherwise (honest)."""
from __future__ import annotations

import subprocess
import shutil
import time
from pathlib import Path


def snapshot(root_mnt: str, name: str = "") -> dict:
    if shutil.which("btrfs"):
        fstype = subprocess.run(["findmnt", "-n", "-o", "FSTYPE", root_mnt],
                                capture_output=True, text=True).stdout.strip()
        if fstype == "btrfs":
            snap = f"{root_mnt}.snapshots/{name or 'recovery-' + str(int(time.time()))}"
            Path(snap).parent.mkdir(parents=True, exist_ok=True)
            out = subprocess.run(["btrfs", "subvolume", "snapshot", root_mnt, snap],
                                 capture_output=True, text=True, timeout=120)
            return {"supported": True, "ok": out.returncode == 0, "snapshot": snap}
    etc = Path(root_mnt) / "etc"
    if etc.exists():
        import tarfile
        out = Path(f"/run/recovery-etc-{int(time.time())}.tar.gz")
        with tarfile.open(out, "w:gz") as tar:
            tar.add(etc, arcname="etc")
        return {"supported": False, "fallback": "tar of /etc", "file": str(out),
                "note": "btrfs snapshots unavailable on this filesystem"}
    return {"supported": False, "reason": "no root mounted"}
