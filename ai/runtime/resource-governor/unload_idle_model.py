"""Idle unload honoring pins."""
from __future__ import annotations


def should_unload(idle_seconds: float, timeout_s: int, pinned: bool) -> bool:
    return not pinned and idle_seconds > timeout_s
