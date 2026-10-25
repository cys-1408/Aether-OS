"""Reset Aether runtime config to distro defaults."""
from __future__ import annotations

import shutil
from pathlib import Path


def reset(root: str) -> dict:
    state = Path(root) / "var/lib/aether/runtime"
    if state.exists():
        shutil.rmtree(state)
    return {"reset": True, "note": "model registry + state cleared; models left in place"}
