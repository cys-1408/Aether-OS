"""FilesystemCreator: wipe signatures, ESP FAT32 + root ext4 (or inside LUKS)."""
from __future__ import annotations

import subprocess
from pathlib import Path

from installer._process import run_argv
from installer.logging.installer_log import InstallerLog


class FilesystemCreator:
    def __init__(self, dry_run: bool = False, log: InstallerLog | None = None):
        self.dry_run = dry_run
        self.log = log or InstallerLog(echo=False)

    # ------------------------------------------------------------------ #
    def resolve_root_partition(self, disk: str, role: str) -> str | None:
        """Return the partition device for role 'esp' or 'root' on this disk."""
        disk_name = Path(disk).name
        base = Path("/dev") / disk_name
        with_suffix = Path(str(base) + "1")
        numbered = Path(f"/dev/{disk_name}1")

        probe = subprocess.run(
            ["lsblk", "-rno", "NAME,PATH,LABEL,PARTLABEL", base],
            capture_output=True, text=True, timeout=30)
        if probe.returncode != 0:
            return None
        entries = []
        for line in probe.stdout.splitlines():
            parts = line.split()
            if len(parts) < 4:
                continue
            entries.append({"name": parts[0], "path": parts[1],
                            "label": parts[2], "partlabel": parts[3]})
        p1 = next((e for e in entries
                   if e["path"] in {str(with_suffix), str(numbered)}
                   or e["name"].endswith("1")), None)
        p2 = next((e for e in entries
                   if e["name"].endswith("2")), None)
        if role == "esp":
            return p1["path"] if p1 else None
        if role == "root":
            return p2["path"] if p2 else None
        return None

    # ------------------------------------------------------------------ #
    def wipe_signatures(self, partition: str) -> dict:
        if self.dry_run:
            return {"wipefs": partition, "dry_run": True}
        res = run_argv(["wipefs", "-a", partition], log=self.log,
                       step="format", dry_run=self.dry_run)
        return {"wipefs": partition, "ok": res.ok}

    def format_esp(self, esp_device: str) -> dict:
        res = run_argv(["mkfs.fat", "-F32", "-n", "AETHER_EFI", esp_device],
                       log=self.log, step="format", dry_run=self.dry_run)
        if not res.ok and not self.dry_run:
            raise RuntimeError(f"mkfs.fat failed: {res.stderr[-800:]}")
        return {"esp": esp_device, "fstype": "vfat", "ok": True}

    def format_root(self, root_device: str) -> dict:
        res = run_argv(["mkfs.ext4", "-L", "AETHEROS", "-E", "nodiscard",
                        root_device],
                       log=self.log, step="format", dry_run=self.dry_run)
        if not res.ok and not self.dry_run:
            raise RuntimeError(f"mkfs.ext4 failed: {res.stderr[-800:]}")
        return {"root": root_device, "fstype": "ext4", "ok": True}

    # Back-compat flat entry point used by installer_controller.
    def make_filesystems(self, disk: str) -> dict:
        esp = self.resolve_root_partition(disk, "esp")
        root = self.resolve_root_partition(disk, "root")
        if not self.dry_run:
            if esp:
                self.wipe_signatures(esp)
            if root:
                self.wipe_signatures(root)
        if esp:
            self.format_esp(esp)
        if root:
            self.format_root(root)
        return {"esp": esp, "root": root, "encrypted_root_skipped":
                self.dry_run or root is None}
