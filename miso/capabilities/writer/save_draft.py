"""save_draft: write content atomically."""
from __future__ import annotations

from pathlib import Path

from aether_core.config import atomic_write_text


def run(params: dict, peer_uid: int = 0) -> dict:
    p = Path(str(params.get("path", ""))).expanduser()
    p.parent.mkdir(parents=True, exist_ok=True)
    atomic_write_text(p, str(params.get("content", "")), mode=0o644)
    return {"path": str(p), "bytes": p.stat().st_size}
