"""Power manager facade: one entry point combining profiles, suspend, battery
and thermal pieces (each real module beneath: power_profiles, battery_policy,
suspend_resume, thermal_policy)."""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))


def _import():
    import power_profiles
    import battery_policy
    import suspend_resume
    import thermal_policy
    return power_profiles, battery_policy, suspend_resume, thermal_policy


def snapshot() -> dict:
    """Actual measured power state for panels/settings (no invented values)."""
    pp, bp, sr, tp = _import()
    return {
        "profiles": sorted(pp.PROFILES),
        "capabilities": pp.capabilities(),
        "battery_energy_state": bp.guidance(),
        "thermal_state": tp.guidance(),
        "suspend_states": sr.supported_states(),
    }


def apply_profile(profile: str) -> dict:
    pp, bp, *_ = _import()
    result = pp.apply(profile)
    if "error" not in result and bp.guidance().get("ac_online") is False \
            and profile == "performance":
        result["note"] = "performance profile on battery: expect faster drain"
    return result


def suspend_now() -> dict:
    sr, *_ = _import()
    return sr.suspend()


__all__ = ["snapshot", "apply_profile", "suspend_now"]
