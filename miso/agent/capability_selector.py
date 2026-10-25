"""Select capabilities from the registry for a plan step."""
from __future__ import annotations


def select(registry: dict, capability_id: str) -> dict | None:
    return registry.get(capability_id)
