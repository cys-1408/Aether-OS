"""copy_file: real copy with bytes count report."""
from __future__ import annotations

import shutil
from pathlib import Path


def run(params: dict, peer_uid: int = 0) -> dict:
    src = Path(str(params.get("src", ""))).expanduser()
    dst = Path(str(params.get("dst", ""))).expanduser()
    if not src.is_file():
        from aether_core.errors import IpcError
        raise IpcError("E_NOT_FOUND", f"not a file: {src}")
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)
    return {"dst": str(dst), "bytes": dst.stat().st_size}
