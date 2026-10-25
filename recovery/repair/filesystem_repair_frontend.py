"""fsck frontend with explicit target confirm."""
from __future__ import annotations

import subprocess


def repair(device: str, confirmed: bool) -> dict:
    if not confirmed:
        return {"repaired": False, "reason": "explicit confirmation required"}
    out = subprocess.run(["fsck", "-y", device], capture_output=True, text=True, timeout=3600)
    return {"repaired": out.returncode in (0, 1), "detail": out.stdout[-400:]}
