"""Companion state -> top bar + panel status mapping."""
from __future__ import annotations

STATE_LABELS = {
    "idle": "All calm", "walking": "Walking over", "running": "Running",
    "jumping": "Jumping", "searching": "Searching", "sleeping": "Napping",
    "carrying": "Carrying something", "pulling": "Stretching", "pushing": "Shrinking",
    "focused": "Guarding focus",
}


def label_for(state: str) -> str:
    return STATE_LABELS.get(state, "All calm")
