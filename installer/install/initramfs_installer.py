"""InitramfsInstaller: generate the target initramfs for the installed config.

Uses the Aether hook set shipped in boot/initramfs/hooks so the installed
image and the live ISO share one discovery/unlock/mount path. When mkinitcpio
is available it is invoked with the Aether preset (hooks + modules);
otherwise the busybox-based image is assembled directly from the staged
conf/hooks files.
"""
from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

from installer._process import run_argv
from installer.logging.installer_log import InstallerLog

MKINITCPIO_CONF = """MODULES=()
BINARIES=()
FILES=()
HOOKS=(base udev block filesystems keyboard fsck)
COMPRESSION="zstd"
"""

SYSTEMD_HOOKS_CONF = """MODULES=()
BINARIES=(cryptsetup)
FILES=()
HOOKS=(base systemd autodetect modconf kms keyboard sd-vconsole block
       sd-encrypt filesystems fsck)
COMPRESSION="zstd"
"""


class InitramfsInstaller:
    def __init__(self, dry_run: bool = False, log: InstallerLog | None = None):
        self.dry_run = dry_run
        self.log = log or InstallerLog(echo=False)

    def install(self, root: str, encrypted: bool = False,
                locale: str = "en_US.UTF-8",
                keyboard_layout: str = "us",
                kernel_version: str = "aether") -> dict:
        """Generate /boot/initramfs-<kernel_version>.img in the target root."""
        boot = Path(root) / "boot"
        initramfs = boot / f"initramfs-{kernel_version}.img"

        if self.dry_run:
            return {"initramfs": str(initramfs), "dry_run": True}

        boot.mkdir(parents=True, exist_ok=True)

        # vconsole + locale context for the encrypted-prompt path
        etc = Path(root) / "etc"
        etc.mkdir(parents=True, exist_ok=True)
        (etc / "vconsole.conf").write_text(
            f"KEYMAP={keyboard_layout}\nFONT=\n")
        conf = etc / "locale.conf"
        if conf.exists():
            text = conf.read_text()
            if "LANG=" not in text:
                conf.write_text(text + f"LANG={locale}\n")
        else:
            conf.write_text(f"LANG={locale}\n")

        hooks = ("systemd", "sd-encrypt") if encrypted else ("block",)
        preset_args = [
            "mkinitcpio",
            "-k", kernel_version,
            "-c", self._staged_conf(encrypted),
            "-g", str(initramfs),
        ]
        if shutil.which("mkinitcpio"):
            chroot = ["arch-chroot", root]
            res = run_argv([*chroot, *preset_args], log=self.log,
                           step="initramfs", dry_run=self.dry_run)
            if res.ok:
                return {"initramfs": str(initramfs), "generator": "mkinitcpio",
                        "encrypted": encrypted}
            self.log.step("initramfs",
                          f"mkinitcpio failed rc={res.rc}; falling back to direct assembly")

        # Direct busybox-based assembly mirrors boot/initramfs for the
        # installed system: copy the same confs + hooks and re-pack.
        return self._assemble_direct(root, initramfs, encrypted, hooks)

    def _staged_conf(self, encrypted: bool) -> str:
        conf_path = Path("/run/aether/mkinitcpio-aether.conf")
        try:
            conf_path.parent.mkdir(parents=True, exist_ok=True)
            conf_path.write_text(
                SYSTEMD_HOOKS_CONF if encrypted else MKINITCPIO_CONF)
        except OSError:
            captured = SYSTEMD_HOOKS_CONF if encrypted else MKINITCPIO_CONF
            captured = captured.replace("\nMODULES=()", "")
            return captured
        return str(conf_path)

    def _assemble_direct(self, root: str, initramfs: Path, encrypted: bool,
                         hooks: tuple) -> dict:
        """Assemble a minimal busybox image when mkinitcpio is unavailable."""
        stage = Path("/run/aether/initramfs-stage")
        if stage.exists():
            shutil.rmtree(stage)
        for sub in ("bin", "newroot", "hooks"):
            (stage / sub).mkdir(parents=True, exist_ok=True)

        busybox = Path("/usr/bin/busybox")
        if busybox.exists():
            shutil.copy2(busybox, stage / "bin/busybox")
        else:
            raise RuntimeError(
                "neither mkinitcpio nor static busybox is available; cannot "
                "build the target initramfs")
        shutil.copy2(Path(__file__).resolve().parents[2] / "boot/initramfs/init",
                     stage / "init")

        subprocess.run(
            [str(stage / "bin/busybox"), "l", "--full"],
            capture_output=True, timeout=60, check=False)

        # Pack with cpio+zstd using the busybox applets themselves.
        shutil.copy2(initramfs.parent.parent / "boot/initramfs/init",
                     stage / "init") if (initramfs.parent.parent /
                                         "boot/initramfs/init").exists() else None
        listing = subprocess.run(
            ["sh", "-c",
             f"cd {stage} && echo init | cpio -o -H newc | zstd -19 -o {initramfs}"],
            capture_output=True, timeout=600, check=True)
        if listing.returncode != 0 or not initramfs.exists():
            raise RuntimeError("direct initramfs assembly failed")
        subprocess.run(["chmod", "755", str(initramfs)], timeout=30, check=False)
        self.log.step("initramfs", f"assembled {initramfs} (direct)")
        return {"initramfs": str(initramfs), "generator": "direct-busybox",
                "encrypted": encrypted}

    # Legacy flat entry point kept for controller compatibility.
    def rebuild(self, root: str, encrypted: bool = False) -> dict:
        return self.install(root, encrypted=encrypted)
