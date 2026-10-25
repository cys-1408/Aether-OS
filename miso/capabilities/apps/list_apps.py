"""Capability list_apps — enumerate installed/running applications via Shell."""

from __future__ import annotations

from miso.capabilities.apps import SHELL_METHODS
from miso.capabilities._shell import shell_call


def execute(params: dict, ctx: dict) -> dict:
    """Ask the Shell for its application list (optionally name-filtered)."""
    if not isinstance(params, dict):
        params = {}
    result = shell_call(ctx["uid"], SHELL_METHODS["list_apps"], {
        "filter": str(params.get("filter", "")) or None,
    })
    apps = result.get("apps", [])
    if params.get("filter") and isinstance(apps, list):
        needle = str(params["filter"]).lower()
        apps = [a for a in apps
                if needle in str(a.get("name", "")).lower()
                or needle in str(a.get("app_id", "")).lower()]
    return {"apps": apps, "count": len(apps)}
