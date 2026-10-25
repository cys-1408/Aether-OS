"""Policy version tracking."""
from __future__ import annotations


def version_of(layer: dict) -> int:
    return int(layer.get("policy_version", 1))
