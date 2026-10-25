"""Mount plan: /mnt target with ESP + API-fs mounts (class API)."""
from __future__ import annotations

import subprocess
from pathlib import Path

from installer.logging.installer_log import InstallerLog
from installer._process import run_argv


class MountPlan:
    def __init__(self, *, encrypted: bool = False, root_device: str = "",
                 esp_device: str | None = None, dry_run: bool = False,
                 log: InstallerLog | None = None):
        self.encrypted = encrypted
        self.root_device = root_device
        self.esp_device = esp_device
        self.dry_run = dry_run
        self.log = log or InstallerLog(echo=False)

    def apply(self) -> dict:
        """Mount root at /mnt and the ESP at /mnt/efi; bind api+runtime dirs."""
        if self.dry_run:
            return {"root": "/mnt", "dry_run": True}
        subprocess.run(["umount", "-R", "/mnt"], check=False,
                       capture_output=True, timeout=120)
        root_dev = self.root_device or "/dev/mapper/aether-root"
        run_argv(["mount", root_dev, "/mnt"], log=self.log, step="mount")
        esp = self.esp_device
        (Path("/mnt/efi")).mkdir(parents=True, exist_ok=True)
        if esp:
            run_argv(["mount", esp, "/mnt/efi"], log=self.log, step="mount")
        for sub in ("proc", "sys", "dev"):
            subprocess.run(["mount", "--rbind", f"/{sub}", f"/mnt/{sub}"],
                           check=False, capture_output=True, timeout=60)
        return {"root": "/mnt", "esp": "/mnt/efi"}

    # Flat-compat wrapper retained for older callers.
    def mount_all(self) -> dict:
        return self.apply()


def mount_all(disk: str, encrypted: bool, dry_run: bool = False) -> dict:
    """Legacy flat entry point (controller compat)."""
    root = "/dev/mapper/aether-root" if encrypted else f"{disk}2"
    esp = f"{disk}1"
    plan = MountPlan(encrypted=encrypted, root_device=root, esp_device=esp,
                     dry_run=dry_run)
    return plan.apply()
