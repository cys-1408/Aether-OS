"""Capability tile_windows — retile visible windows via the Shell."""

from __future__ import annotations

from miso.capabilities._shell import shell_call
from miso.capabilities.windows import SHELL_METHODS


def execute(params: dict, ctx: dict) -> dict:
    """Tile all visible windows (direction hint optional)."""
    direction = str(params.get("direction", "auto"))
    result = shell_call(ctx["uid"], SHELL_METHODS["tile_windows"],
                        {"direction": direction}, timeout=25.0)
    return {
        "tiled": result.get("tiled", result.get("count", 0)),
        "direction": direction,
    }
