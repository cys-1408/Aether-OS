"""Recovery environment status."""
from __future__ import annotations


def status() -> dict:
    import shutil
    return {"tools": {"cryptsetup": bool(shutil.which("cryptsetup")),
                      "pacman": bool(shutil.which("pacman")),
                      "grub": bool(shutil.which("grub-install"))},
            "network_required": False}
