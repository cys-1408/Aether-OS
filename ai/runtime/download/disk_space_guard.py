"""Guard: stop before exhausting the filesystem."""
from __future__ import annotations

import shutil
from pathlib import Path

from aether_core.errors import IpcError


def guard(target: Path, needed_bytes: int) -> dict:
    free = shutil.disk_usage(target if target.exists() else target.parent).free
    if free < int(needed_bytes * 1.2):
        raise IpcError("E_DISK_SPACE", f"free {free/1e9:.1f}GB < required {(needed_bytes*1.2)/1e9:.1f}GB")
    return {"free_bytes": free}
