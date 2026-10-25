"""Static validation of user-supplied rule specs."""
from __future__ import annotations


def validate_rule(spec: dict) -> dict:
    errors = []
    action = spec.get("action")
    if action not in ("accept", "drop", "reject"):
        errors.append("action must be accept|drop|reject")
    proto = spec.get("protocol")
    if proto not in ("tcp", "udp", None):
        errors.append("protocol must be tcp|udp")
    port = spec.get("port")
    if port is not None and not (isinstance(port, int) and 1 <= port <= 65535):
        errors.append("port must be 1-65535")
    return {"valid": not errors, "errors": errors}
