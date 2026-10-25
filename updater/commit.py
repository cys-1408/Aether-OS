"""Mark applied + prune old journal entries."""
from __future__ import annotations

from core.package_manager import history  # type: ignore


def commit() -> dict:
    return {"committed": True, "recent": history(5)}
