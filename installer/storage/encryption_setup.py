"""EncryptionSetup: LUKS2 (argon2id) format/open/UUID for the root partition."""
from __future__ import annotations

import subprocess

from installer._process import run_argv
from installer.logging.installer_log import InstallerLog
from installer.logging.secret_filter import register_secret

MAPPER = "/dev/mapper/aether-root"


class EncryptionSetup:
    def __init__(self, dry_run: bool = False, log: InstallerLog | None = None):
        self.dry_run = dry_run
        self.log = log or InstallerLog(echo=False)

    # ------------------------------------------------------------------ #
    def luks_format(self, partition: str, passphrase: str) -> dict:
        register_secret(passphrase)
        if self.dry_run:
            return {"mapper": MAPPER, "dry_run": True}
        # Format: pass twice (re-type) via stdin keys; not via argv.
        res = run_argv(["cryptsetup", "luksFormat", "--type", "luks2",
                        "--pbkdf", "argon2id", partition],
                       log=self.log, step="encrypt", dry_run=self.dry_run,
                       input_bytes=(passphrase + "\n" + passphrase + "\n")
                       .encode("utf-8"))
        if not res.ok:
            raise RuntimeError(f"luksFormat failed: {res.stderr[-800:]}")
        return {"mapper": MAPPER, "partition": partition}

    def luks_open(self, partition: str, passphrase: str) -> dict:
        register_secret(passphrase)
        if self.dry_run:
            return {"mapper": MAPPER, "dry_run": True}
        subprocess.run(["cryptsetup", "close", "aether-root"], check=False,
                       capture_output=True, timeout=30)
        res = run_argv(["cryptsetup", "open", partition, "aether-root"],
                       log=self.log, step="encrypt", dry_run=self.dry_run,
                       input_bytes=(passphrase + "\n").encode("utf-8"))
        if not res.ok:
            raise RuntimeError(f"cryptsetup open failed: {res.stderr[-800:]}")
        return {"mapper": MAPPER}

    def luks_uuid(self, partition: str) -> str:
        """Real LUKS header UUID for crypttab."""
        if self.dry_run:
            return ""
        out = subprocess.run(["cryptsetup", "luksUUID", partition],
                             capture_output=True, text=True, timeout=30)
        return out.stdout.strip()

    # Flat-compat entry point (used by installer_controller / screens).
    def format_and_open(self, disk: str, passphrase: str,
                        *, dry_run: bool = False) -> dict:
        partition = disk.rstrip("/0123456789") + "2"
        self.luks_format(partition, passphrase)
        self.luks_open(partition, passphrase)
        return {"mapper": MAPPER}


def luks_format(disk: str, passphrase: str, dry_run: bool = False) -> dict:
    """Flat wrapper retained for the controller's legacy path."""
    return EncryptionSetup(dry_run=dry_run).format_and_open(disk, passphrase)
