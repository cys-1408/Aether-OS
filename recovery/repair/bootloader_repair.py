"""GRUB reinstall (UEFI + BIOS paths)."""
from __future__ import annotations

import subprocess


def repair(root: str, efi: bool = True) -> dict:
    if efi:
        subprocess.run(["arch-chroot", root, "grub-install", "--target=x86_64-efi",
                        "--efi-directory=/efi", "--bootloader-id=AETHEROS"],
                       check=False, timeout=600)
    else:
        subprocess.run(["arch-chroot", root, "grub-install", "/dev/sda"], check=False, timeout=600)
    subprocess.run(["arch-chroot", root, "grub-mkconfig", "-o", "/boot/grub/grub.cfg"],
                   check=False, timeout=300)
    return {"repaired": True, "mode": "efi" if efi else "bios"}
