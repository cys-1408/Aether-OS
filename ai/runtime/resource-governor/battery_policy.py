"""Battery-aware background inference policy."""
from __future__ import annotations

from power_thermal_profile import power_state  # noqa: F401


def background_allowed(config: dict) -> bool:
    if not config.get("battery", {}).get("pause_background_inference", True):
        return True
    return power_state().get("ac_online") is not False
