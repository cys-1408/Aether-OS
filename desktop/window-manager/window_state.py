"""WindowInfo model used across shell surfaces."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class WindowInfo:
    id: int
    app_id: str
    title: str | None
    workspace: str | None
    focused: bool
    floating: bool
    geometry: dict | None = None
