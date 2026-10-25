"""Kernel downgrade from the pacman cache (real offline rollback)."""
from __future__ import annotations

import subprocess
from pathlib import Path


def list_cached_kernels(root: str) -> list[str]:
    cache = Path(root) / "var/cache/pacman/pkg"
    return sorted({p.name for p in cache.glob("linux-aether-*.pkg.tar.*")})


def downgrade(root: str) -> dict:
    kernels = list_cached_kernels(root)
    if len(kernels) < 1:
        return {"downgraded": False, "reason": "no cached kernel packages"}
    pkg = kernels[0]
    out = subprocess.run(["arch-chroot", root, "pacman", "-U", f"/var/cache/pacman/pkg/{pkg}", "--noconfirm"],
                         capture_output=True, text=True, timeout=1200)
    return {"downgraded": out.returncode == 0, "package": pkg}
