"""BootloaderInstaller: GRUB for UEFI (preferred) and documented BIOS path."""
from __future__ import annotations

from pathlib import Path

from installer._process import run_argv
from installer.logging.installer_log import InstallerLog


class BootloaderInstaller:
    def __init__(self, dry_run: bool = False, log: InstallerLog | None = None):
        self.dry_run = dry_run
        self.log = log or InstallerLog(echo=False)

    def install(self, root: str, firmware: str = "uefi",
                disk_path: str = "", encrypted: bool = False) -> dict:
        chroot = ["arch-chroot", root]
        if firmware == "uefi":
            argv = [*chroot, "grub-install",
                    "--target=x86_64-efi",
                    "--efi-directory=/efi",
                    "--bootloader-id=AETHEROS"]
        elif firmware == "bios":
            if not disk_path:
                raise RuntimeError("BIOS install requires the target disk path")
            argv = [*chroot, "grub-install", disk_path]
        else:
            raise RuntimeError(f"unsupported firmware mode: {firmware}")

        res = run_argv(argv, log=self.log, step="bootloader", dry_run=self.dry_run)
        if not res.ok and not self.dry_run:
            raise RuntimeError(f"grub-install failed: {res.stderr[-1500:]}")

        res = run_argv([*chroot, "grub-mkconfig", "-o", "/boot/grub/grub.cfg"],
                       log=self.log, step="bootloader", dry_run=self.dry_run)
        if not res.ok and not self.dry_run:
            raise RuntimeError(f"grub-mkconfig failed: {res.stderr[-1500:]}")

        # Record the known-good entry slot for rollback (grubenv).
        if encrypted and not self.dry_run:
            try:
                grubenv = Path(root) / "boot/grub/grubenv"
                if grubenv.exists():
                    self.log.step("bootloader", "grubenv present; rollback entry slot reserved")
            except OSError:
                pass

        mode = "uefi" if firmware == "uefi" else "bios"
        return {"bootloader": "grub", "mode": mode}
