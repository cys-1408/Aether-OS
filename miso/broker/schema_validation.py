"""Validate request params against the capability's input schema."""
from __future__ import annotations

from aether_core import validate
from aether_core.errors import IpcError


def validate_params(cap: dict, params: dict) -> None:
    try:
        validate(params, cap.get("input_schema") or {"type": "object"})
    except Exception as e:  # AetherError carries the path
        raise IpcError("E_SCHEMA", f"params invalid: {e}")
