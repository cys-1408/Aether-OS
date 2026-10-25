"""Capability arrange_windows — apply an explicit window layout via the Shell."""

from __future__ import annotations

from aether_core.errors import AetherError

from miso.capabilities._shell import shell_call
from miso.capabilities.windows import SHELL_METHODS

_ALLOWED_LAYOUT_KEYS = {"window_id", "x", "y", "width", "height", "workspace"}


def execute(params: dict, ctx: dict) -> dict:
    """Move/resize windows to the requested layout (schema-validated upstream)."""
    layout = params.get("layout")
    if not isinstance(layout, list) or not layout:
        raise AetherError("invalid_params", "arrange_windows requires a non-empty layout list")
    for item in layout:
        if not isinstance(item, dict) or "window_id" not in item:
            raise AetherError("invalid_params", "each layout item needs window_id")
        unknown = set(item) - _ALLOWED_LAYOUT_KEYS
        if unknown:
            raise AetherError("invalid_params",
                              f"layout item has unexpected keys: {sorted(unknown)}")
    result = shell_call(ctx["uid"], SHELL_METHODS["arrange_windows"],
                        {"layout": layout}, timeout=25.0)
    arranged = result.get("arranged", len(layout))
    return {"arranged": arranged, "requested": len(layout),
            "detail": {k: v for k, v in result.items() if k != "arranged"}}
