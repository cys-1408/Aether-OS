"""Capability close_app — close an application's windows through the Shell."""

from __future__ import annotations

from aether_core.errors import AetherError

from miso.capabilities.apps import SHELL_METHODS
from miso.capabilities._shell import shell_call


def execute(params: dict, ctx: dict) -> dict:
    """Close all windows of one application."""
    app_id = str(params.get("app_id", "")).strip()
    if not app_id:
        raise AetherError("missing_param", "close_app requires app_id")
    result = shell_call(ctx["uid"], SHELL_METHODS["close_app"], {"app_id": app_id})
    return {
        "app_id": app_id,
        "closed": bool(result.get("closed", result.get("ok", True))),
        "windows_closed": result.get("windows_closed"),
    }
