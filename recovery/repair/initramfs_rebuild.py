"""initramfs rebuild from the installed configuration and modules.

Regenerates the target initramfs using the installed kernel version; the
encrypted-root hook set is selected explicitly, mirroring the installer path.
Source config, kernel and modules are never modified.
"""
from __future__ import annotations

import subprocess
from pathlib import Path


def detect_kernel_version(root: str = "/") -> str:
    boot = Path(root) / "boot"
    candidates = sorted(boot.glob("vmlinuz-*"))
    if not candidates:
        return "aether"
    return candidates[0].name.replace("vmlinuz-", "")


def rebuild_initramfs(root: str = "/", kernel_version: str | None = None,
                      encrypted: bool = False) -> dict:
    """Rebuild /boot/initramfs-<kver>.img; returns an honest result."""
    if kernel_version is None:
        kernel_version = detect_kernel_version(root)
    boot = Path(root) / "boot"
    img = boot / f"initramfs-{kernel_version}.img"
    chroot = [] if root == "/" else ["arch-chroot", root]

    if encrypted:
        hooks = ("base systemd autodetect modconf kms keyboard sd-vconsole "
                 "block sd-encrypt filesystems fsck")
    else:
        hooks = "base udev block keyboard filesystems fsck"
    conf = Path("/run/aether/mkinitcpio-recovery.conf")
    conf.write_text(
        "MODULES=()\nBINARIES=(cryptsetup)\nFILES=()\n"
        f"HOOKS=({hooks})\nCOMPRESSION=\"zstd\"\n")
    out = subprocess.run([*chroot, "mkinitcpio", "-k", kernel_version,
                          "-c", str(conf), "-g", str(img)],
                         capture_output=True, text=True, timeout=600)
    if out.returncode != 0:
        return {"rebuilt": False, "reason": out.stderr[-800:]}
    return {"rebuilt": True, "image": str(img),
            "kernel_version": kernel_version, "encrypted": encrypted}
