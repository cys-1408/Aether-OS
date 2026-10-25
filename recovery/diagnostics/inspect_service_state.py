"""Failed units in the installed root."""
from __future__ import annotations

import subprocess


def failed_units(root: str) -> list[str]:
    out = subprocess.run(["arch-chroot", root, "systemctl", "--failed", "--no-legend"],
                         capture_output=True, text=True, timeout=60)
    return [l.split()[0] for l in out.stdout.splitlines() if l.strip()]
