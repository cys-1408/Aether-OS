"""rename_file: same-directory rename."""
from __future__ import annotations

from pathlib import Path


def run(params: dict, peer_uid: int = 0) -> dict:
    p = Path(str(params.get("path", ""))).expanduser()
    new = p.with_name(str(params.get("new_name", "")))
    if new.exists():
        from aether_core.errors import IpcError
        raise IpcError("E_CONFLICT", f"target exists: {new}")
    p.rename(new)
    return {"new_path": str(new)}
