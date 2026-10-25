"""aether-power-manager — profiles, suspend, battery/thermal guidance."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
sys.path.insert(0, Path(__file__).resolve().parents[4].as_posix() + "/libraries/libaether-core/python")

from service_main import SystemService  # noqa: E402
from power_profiles import PROFILES, apply, capabilities  # noqa: E402
from suspend_resume import suspend, supported_states  # noqa: E402
from battery_policy import guidance as battery_guidance  # noqa: E402
from thermal_policy import guidance as thermal_guidance  # noqa: E402


def build_service() -> SystemService:
    return SystemService("power-manager", "power-manager", {
        "Power.status": lambda p: {"profiles": list(PROFILES), "capabilities": capabilities(),
                                   "battery": battery_guidance(), "thermal": thermal_guidance()},
        "Power.profiles": lambda p: {"profiles": list(PROFILES), "capabilities": capabilities()},
        "Power.set_profile": lambda p: apply(str(p.get("profile", "balanced"))),
        "Power.suspend": lambda p: suspend(),
        "Power.battery": lambda p: battery_guidance(),
        "Power.thermal": lambda p: thermal_guidance(),
        "Power.states": lambda p: {"states": supported_states()},
    })


if __name__ == "__main__":
    build_service().run()
