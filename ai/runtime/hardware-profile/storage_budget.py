"""Storage budget checks before large downloads."""
from __future__ import annotations

import shutil
from pathlib import Path

from aether_core.errors import IpcError


def ensure_space(target_dir: Path, needed_bytes: int, *, multiplier: float = 1.2) -> dict:
    target_dir.mkdir(parents=True, exist_ok=True)
    free = shutil.disk_usage(target_dir).free
    required = int(needed_bytes * multiplier)
    if free < required:
        raise IpcError("E_DISK_SPACE", f"insufficient space: need {required/1e9:.1f}GB, free {free/1e9:.1f}GB")
    return {"free_bytes": free, "required_bytes": required, "ok": True}
