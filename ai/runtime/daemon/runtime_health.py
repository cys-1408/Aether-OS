"""Runtime health publication to /run/aether/health-runtime.json."""
from __future__ import annotations

from aether_core.config import atomic_write_json


def publish(state: str, reason: str | None, backend: dict | None) -> None:
    try:
        from pathlib import Path
        atomic_write_json(Path(f"/run/aether/health-runtime.json"),
                          {"name": "runtime", "state": state, "reason": reason,
                           "backend": backend, "last_error": reason}, mode=0o644)
    except OSError:
        pass
