"""Capability list_windows — enumerate the user's windows via the Shell."""

from __future__ import annotations

from miso.capabilities._shell import shell_call
from miso.capabilities.windows import SHELL_METHODS


def execute(params: dict, ctx: dict) -> dict:
    """Return the current window list (id, app, title, geometry, focus)."""
    result = shell_call(ctx["uid"], SHELL_METHODS["list_windows"], {})
    windows = result.get("windows", [])
    return {"windows": windows, "count": len(windows) if isinstance(windows, list) else 0}
