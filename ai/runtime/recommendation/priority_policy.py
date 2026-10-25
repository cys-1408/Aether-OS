"""Priority policy for recommendations (quality vs speed vs energy)."""
from __future__ import annotations


def order_key(model: dict, priority: str = "balanced") -> tuple:
    size = float(model.get("approx_size_gb") or 0)
    if priority == "speed":
        return (size,)
    if priority == "quality":
        return (-size,)
    return (abs(size - 1.5),)  # balanced: prefer ~1.5B class
