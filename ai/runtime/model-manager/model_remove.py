"""Safe removal with reclaimed-space report."""
from __future__ import annotations

import shutil
from pathlib import Path

from model_registry import ModelRegistry


def remove_model(registry: ModelRegistry, store_dir: Path, model_id: str) -> dict:
    result = registry.remove(model_id)
    model_dir = store_dir / model_id
    reclaimed = 0
    if model_dir.exists():
        total = sum(f.stat().st_size for f in model_dir.rglob("*") if f.is_file())
        shutil.rmtree(model_dir)
        reclaimed = total
    return result | {"reclaimed_bytes": reclaimed}
