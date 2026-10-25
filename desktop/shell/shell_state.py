"""Shell state dataclasses."""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class ShellState:
    focus_active: bool = False
    focus_remaining: int | None = None
    miso_state: str = "idle"
    panel_open: bool = False
    degraded_services: list[str] = field(default_factory=list)
