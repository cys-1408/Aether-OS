"""THE destructive guard: typed confirmation + pre-install table backup.

The vulnerable moment of the installer: touching a disk that might not be the one
 on screen. Mitigation chain, each step independent:
 1. typed confirmation: user re-types the target kernel name (e.g. "sda")
 2. identity snapshot: serial/model recorded before the plan is built...
 3. ...and verified immediately before the first destructive write
 4. table backup so `install_rollback` can restore exactly what existed
"""
from __future__ import annotations

import subprocess
import time
from pathlib import Path

from aether_core import paths

BACKUPS = paths.SYSTEM_STATE_DIR / "installer" / "partition-table-backups"


def disk_identity(disk: str) -> dict:
    out = subprocess.run(
        ["lsblk", "-nro", "ID_SERIAL,ID_MODEL,SIZE,NAME",
         Path(disk)],
        capture_output=True, text=True, timeout=30)
    parts = out.stdout.split()
    if not parts:
        return {}
    return {"serial": parts[0] if parts else "",
            "model": parts[1] if len(parts) > 1 else "",
            "size": parts[2] if len(parts) > 2 else "",
            "name": disk.rstrip("/").split("/")[-1]}


def require_confirmation(disk: str, typed: str) -> None:
    expected = disk.rstrip("/").split("/")[-1]
    if typed.strip() != expected:
        raise PermissionError(f"typed confirmation mismatch — refusing to touch {disk}")


def backup_partition_table(disk: str) -> Path:
    BACKUPS.mkdir(parents=True, exist_ok=True)
    stamp = time.strftime("%Y%m%d-%H%M%S")
    out = BACKUPS / f"{Path(disk).name}-{stamp}.sfdisk"
    dump = subprocess.run(["sfdisk", "--dump", disk], capture_output=True,
                          text=True, timeout=30)
    out.write_text(dump.stdout)
    return out


class DestructiveActionGuard:
    """Guard object attached to the controller from the summary screen."""

    def __init__(self):
        self.identity: dict = {}
        self.disk: str = ""
        self.layer: list[str] = []

    def arm(self, disk: str) -> dict:
        self.disk = disk
        self.identity = disk_identity(disk)
        self.layer.append("identity-armed")
        return dict(self.identity)

    def refresh(self) -> dict:
        if self.disk:
            self.identity = disk_identity(self.disk)
        return dict(self.identity)

    def verify(self) -> dict:
        if not self.disk:
            return {"ok": True, "note": "no disk armed"}
        current = disk_identity(self.disk)
        if current.get("serial") and current["serial"] != self.identity.get("serial"):
            return {"ok": False,
                    "reason": f"disk {self.disk} changed identity: "
                              f"{self.identity.get('serial')} -> {current.get('serial')}"}
        return {"ok": True, "identity": current}

    def typed_confirmation(self, typed: str) -> None:
        require_confirmation(self.disk, typed)
        self.layer.append("typed-confirmed")


def typed_confirmation(disk: str, typed: str) -> None:
    require_confirmation(disk, typed)
