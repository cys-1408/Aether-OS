"""Taskbar state model."""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class TaskbarState:
    running: set[str] = field(default_factory=set)
    focused: str | None = None
