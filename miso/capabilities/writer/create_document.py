"""create_document: real file in ~/Documents opened by Writer."""
from __future__ import annotations

import subprocess
from pathlib import Path

from aether_core.config import atomic_write_text


def run(params: dict, peer_uid: int = 0) -> dict:
    docs = Path.home() / "Documents"
    docs.mkdir(exist_ok=True)
    name = str(params.get("name", "")).strip() or f"note-{int(__import__('time').time())}.md"
    target = docs / name
    i = 2
    while target.exists():
        target = docs / f"{Path(name).stem} ({i}){Path(name).suffix}"
        i += 1
    atomic_write_text(target, str(params.get("content", "")), mode=0o644)
    try:
        subprocess.Popen(["aether-writer", "--open", str(target)])
    except FileNotFoundError:
        pass
    return {"path": str(target)}
