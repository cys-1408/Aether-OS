"""Restore skel defaults for chosen dotfiles (with .bak originals)."""
from __future__ import annotations

import shutil
from pathlib import Path


def repair(root: str, username: str, files: list[str]) -> dict:
    home = Path(root) / "home" / username
    skel = Path(root) / "etc/skel"
    restored = []
    for f in files:
        src, dst = skel / f, home / f
        if src.exists():
            if dst.exists():
                shutil.copy2(dst, dst.with_suffix(dst.suffix + ".pre-repair.bak"))
            shutil.copy2(src, dst)
            restored.append(f)
    return {"restored": restored}
