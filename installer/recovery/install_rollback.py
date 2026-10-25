"""Install rollback: restore the pre-install partition table + close mappers."""
from __future__ import annotations

import subprocess
from pathlib import Path

from installer._process import run_argv
from installer.logging.installer_log import InstallerLog
from installer.storage.destructive_action_guard import BACKUPS


class InstallRollback:
    def __init__(self, dry_run: bool = False, log: InstallerLog | None = None):
        self.dry_run = dry_run
        self.log = log or InstallerLog(echo=False)

    def rollback(self, *, disk_path: str, table_backup: Path | None,
                 luks_created: bool, luks_partition: str | None,
                 luks_passphrase: str | None) -> dict:
        note = []
        subprocess.run(["umount", "-R", "/mnt"], check=False,
                       capture_output=True, timeout=120)
        if luks_created and luks_partition:
            res = run_argv(["cryptsetup", "close", "aether-root"],
                           log=self.log, step="rollback",
                           dry_run=self.dry_run)
            note.append(f"mapper closed: rc={res.rc}")
        elif not luks_created:
            note.append("no LUKS volume created; nothing to close")

        if table_backup and table_backup.exists() and not self.dry_run:
            res = run_argv(["sfdisk", "--force", disk_path],
                           log=self.log, step="rollback", dry_run=False,
                           input_bytes=table_backup.read_bytes())
            if res.ok:
                run_argv(["partprobe", disk_path], log=self.log,
                         step="rollback")
                note.append(f"table restored from {table_backup.name}")
            else:
                note.append(f"table restore failed: {res.stderr[-300:]}")
        elif self.dry_run:
            note.append("dry-run rollback (no changes)")
        else:
            note.append("no table backup found; leave disk as-is")

        return {"rolled_back": True, "notes": note}


def backup_partition_table(disk: str, *, dry_run: bool = False,
                           log: InstallerLog | None = None) -> Path:
    """Save the current table before any destructive change."""
    import time
    if log is None:
        log = InstallerLog(echo=False)
    back_dir = Path(BACKUPS)
    back_dir.mkdir(parents=True, exist_ok=True)
    stamp = time.strftime("%Y%m%d-%H%M%S")
    out = back_dir / f"{Path(disk).name}-{stamp}.sfdisk"
    if not dry_run:
        dump = subprocess.run(["sfdisk", "--dump", disk],
                              capture_output=True, text=True, timeout=30)
        out.write_text(dump.stdout)
        log.step("backup-table", f"saved {out}")
    return out
