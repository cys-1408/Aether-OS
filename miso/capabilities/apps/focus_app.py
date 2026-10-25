"""Capability focus_app — raise and focus an application via the Shell."""

from __future__ import annotations

from aether_core.errors import AetherError

from miso.capabilities.apps import SHELL_METHODS
from miso.capabilities._shell import shell_call


def execute(params: dict, ctx: dict) -> dict:
    """Focus the most relevant window of one application."""
    app_id = str(params.get("app_id", "")).strip()
    if not app_id:
        raise AetherError("missing_param", "focus_app requires app_id")
    result = shell_call(ctx["uid"], SHELL_METHODS["focus_app"], {"app_id": app_id})
    return {
        "app_id": app_id,
        "focused": bool(result.get("focused", result.get("ok", True))),
    }
