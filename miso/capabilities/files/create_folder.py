"""create_folder: mkdir -p within scope."""
from __future__ import annotations

from pathlib import Path


def run(params: dict, peer_uid: int = 0) -> dict:
    p = Path(str(params.get("path", ""))).expanduser()
    p.mkdir(parents=True, exist_ok=False)
    return {"path": str(p), "created": True}
