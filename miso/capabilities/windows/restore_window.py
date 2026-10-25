"""Capability restore_window — restore a minimized window via the Shell."""

from __future__ import annotations

from aether_core.errors import AetherError

from miso.capabilities._shell import shell_call
from miso.capabilities.windows import SHELL_METHODS


def execute(params: dict, ctx: dict) -> dict:
    """Restore the window with the given compositor id."""
    window_id = params.get("window_id")
    if not isinstance(window_id, int) or window_id < 1:
        raise AetherError("invalid_params", "restore_window requires integer window_id >= 1")
    result = shell_call(ctx["uid"], SHELL_METHODS["restore_window"],
                        {"window_id": window_id})
    return {"window_id": window_id,
            "restored": bool(result.get("restored", result.get("ok", True)))}
