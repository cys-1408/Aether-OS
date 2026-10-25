"""Per-output scaling helpers (fractions allowed by sway)."""
from __future__ import annotations

from display_manager import set_scale


def set_ui_scale(output: str, scale: float) -> dict:
    if not (0.5 <= scale <= 3.0):
        return {"ok": False, "error": "scale must be 0.5-3.0"}
    return set_scale(output, scale)
