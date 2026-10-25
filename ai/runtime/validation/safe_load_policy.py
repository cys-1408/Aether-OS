"""Safe load policy: refuse weird files (no exec bit tricks, size sanity)."""
from __future__ import annotations

from pathlib import Path


def safe_to_load(path: Path) -> dict:
    if path.suffix not in (".gguf",):
        return {"ok": False, "reason": "only gguf models load"}
    size = path.stat().st_size if path.exists() else 0
    if size < 1_000_000:
        return {"ok": False, "reason": "file too small to be a model"}
    return {"ok": True}
