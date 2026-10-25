"""Capability create_workspace — create a compositor workspace via the Shell."""

from __future__ import annotations

import re

from aether_core.errors import AetherError

from miso.capabilities.apps import SHELL_METHODS
from miso.capabilities._shell import shell_call


def execute(params: dict, ctx: dict) -> dict:
    """Create an extra named workspace."""
    name = str(params.get("name", "")).strip()
    if not name:
        raise AetherError("missing_param", "create_workspace requires name")
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9 _-]{0,59}", name):
        raise AetherError("invalid_params",
                          "workspace name must be 1-60 chars of letters, digits, space, '-', '_'")
    result = shell_call(ctx["uid"], SHELL_METHODS["create_workspace"], {"name": name})
    return {
        "name": name,
        "created": bool(result.get("created", result.get("ok", True))),
        "workspace_index": result.get("workspace_index"),
    }
