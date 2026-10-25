"""open_file: launch with the default application (gio)."""
from __future__ import annotations

import subprocess
from pathlib import Path


def run(params: dict, peer_uid: int = 0) -> dict:
    p = Path(str(params.get("path", ""))).expanduser()
    if not p.exists():
        from aether_core.errors import IpcError
        raise IpcError("E_NOT_FOUND", f"not found: {p}")
    try:
        subprocess.Popen(["gio", "open", str(p)])
        return {"opened": True, "path": str(p)}
    except FileNotFoundError:
        return {"opened": False, "error": "gio not available"}
