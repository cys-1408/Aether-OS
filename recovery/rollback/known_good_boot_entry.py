"""Manage the known-good GRUB entry via grubenv saved_entry."""
from __future__ import annotations

import subprocess
from pathlib import Path


def mark_known_good(root: str) -> dict:
    env = Path(root) / "boot/grub/grubenv"
    if env.exists():
        subprocess.run(["grub-editenv", str(env), "set", "saved_entry=1"], check=False, timeout=30)
        return {"known_good": "entry 1"}
    return {"known_good": False, "reason": "grubenv missing"}
