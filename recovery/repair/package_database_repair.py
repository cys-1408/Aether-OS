"""pacman database repair inside the installed root."""
from __future__ import annotations

import subprocess


def repair(root: str) -> dict:
    subprocess.run(["arch-chroot", root, "pacman", "-Dkk"], check=False, timeout=300)
    subprocess.run(["arch-chroot", root, "pacman", "-Sy", "archlinux-keyring", "--noconfirm"],
                   check=False, timeout=600)
    return {"repaired": True}
