"""Thermal throttle/pause policy."""
from __future__ import annotations

from power_thermal_profile import thermal_state  # noqa: F401


def inference_allowed() -> str:
    state = thermal_state()
    return {"critical": "pause", "hot": "throttle"}.get(state, "run")
