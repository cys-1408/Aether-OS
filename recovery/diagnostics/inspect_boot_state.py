"""Boot state via bootctl/efibootmgr (real)."""
from __future__ import annotations

import subprocess


def boot_state() -> dict:
    out = {}
    for tool, argv in (("bootctl", ["bootctl", "status"]), ("efibootmgr", ["efibootmgr"])):
        try:
            r = subprocess.run(argv, capture_output=True, text=True, timeout=15)
            out[tool] = r.stdout[:800] if r.returncode == 0 else None
        except FileNotFoundError:
            out[tool] = None
    return out
