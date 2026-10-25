"""Task cancellation registry."""
from __future__ import annotations

_active: set[str] = set()


def mark(task_id: str) -> None:
    _active.add(task_id)


def is_cancelled(task_id: str) -> bool:
    return task_id in _active
