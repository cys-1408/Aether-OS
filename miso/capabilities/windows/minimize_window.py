"""Capability minimize_window — minimize one window via the Shell."""

from __future__ import annotations

from aether_core.errors import AetherError

from miso.capabilities._shell import shell_call
from miso.capabilities.windows import SHELL_METHODS


def execute(params: dict, ctx: dict) -> dict:
    """Minimize the window with the given compositor id."""
    window_id = params.get("window_id")
    if not isinstance(window_id, int) or window_id < 1:
        raise AetherError("invalid_params", "minimize_window requires integer window_id >= 1")
    result = shell_call(ctx["uid"], SHELL_METHODS["minimize_window"],
                        {"window_id": window_id})
    return {"window_id": window_id,
            "minimized": bool(result.get("minimized", result.get("ok", True)))}
