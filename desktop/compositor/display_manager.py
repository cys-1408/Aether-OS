"""Display/monitor management via sway outputs."""
from __future__ import annotations

import json

from compositor_adapter import CompositorAdapter


def outputs() -> list[dict]:
    try:
        tree = CompositorAdapter().tree()
        return [o for o in (tree or {}).get("nodes", []) if o.get("type") == "output"]
    except Exception:
        return []


def set_mode(output: str, mode: str) -> dict:
    return CompositorAdapter().run(f"output {output} mode {mode}")


def set_scale(output: str, scale: float) -> dict:
    return CompositorAdapter().run(f"output {output} scale {scale}")


def set_position(output: str, x: int, y: int) -> dict:
    return CompositorAdapter().run(f"output {output} position {x} {y}")
