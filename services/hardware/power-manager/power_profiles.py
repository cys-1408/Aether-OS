"""Power profile switching through real kernel interfaces."""
from __future__ import annotations

from pathlib import Path

CPUFREQ_GOV = Path("/sys/devices/system/cpu/cpu0/cpufreq/scaling_governor")
PLATFORM_PROFILE = Path("/sys/firmware/acpi/platform_profile")

PROFILES = {
    "performance": {"governor": "performance", "platform_profile": "performance"},
    "balanced": {"governor": "schedutil", "platform_profile": "balanced"},
    "power-saver": {"governor": "powersave", "platform_profile": "low-power"},
}


def capabilities() -> dict:
    return {
        "cpufreq_governor": CPUFREQ_GOV.exists(),
        "platform_profile": PLATFORM_PROFILE.exists(),
    }


def apply(profile: str) -> dict:
    spec = PROFILES.get(profile)
    if not spec:
        from aether_core.errors import IpcError
        raise IpcError("E_INVALID", f"unknown profile: {profile}")
    applied = []
    try:
        cpus = sorted(Path("/sys/devices/system/cpu").glob("cpu[0-9]*"))
        for cpu in cpus:
            gov = cpu / "cpufreq" / "scaling_governor"
            if gov.exists():
                gov.write_text(spec["governor"] + "\n")
                applied.append(str(gov))
    except (OSError, PermissionError) as e:
        return {"applied": applied, "error": f"{e} (needs root via polkit helper)"}
    if PLATFORM_PROFILE.exists():
        try:
            PLATFORM_PROFILE.write_text(spec["platform_profile"] + "\n")
            applied.append(str(PLATFORM_PROFILE))
        except (OSError, PermissionError) as e:
            return {"applied": applied, "error": f"{e} (needs root via polkit helper)"}
    return {"applied": applied, "profile": profile, "capabilities": capabilities()}
