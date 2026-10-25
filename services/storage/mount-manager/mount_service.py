"""Real mount operations via udisks2 (udisksctl)."""
from __future__ import annotations

import re
import subprocess


def _run(argv: list[str], timeout: int = 15) -> subprocess.CompletedProcess:
    return subprocess.run(argv, capture_output=True, text=True, timeout=timeout)


def mount(device: str) -> dict:
    if not re.fullmatch(r"/dev/[A-Za-z0-9/]+", device):
        return {"ok": False, "error": "invalid device path"}
    try:
        out = _run(["udisksctl", "mount", "-b", device])
        if out.returncode == 0:
            m = re.search(r"mounted at (.+)", out.stdout)
            return {"ok": True, "mountpoint": m.group(1).strip() if m else None}
        return {"ok": False, "error": out.stderr.strip() or out.stdout.strip()}
    except FileNotFoundError:
        return {"ok": False, "error": "udisksctl not installed"}


def unmount(device: str) -> dict:
    try:
        out = _run(["udisksctl", "unmount", "-b", device])
        return {"ok": out.returncode == 0, "error": None if out.returncode == 0 else out.stderr.strip()}
    except FileNotFoundError:
        return {"ok": False, "error": "udisksctl not installed"}
