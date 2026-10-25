"""Timezone list + set (see clock_service)."""
from clock_service import timezone_info, set_timezone, now  # noqa: F401


def list_timezones(limit: int = 0) -> list[str]:
    import subprocess
    try:
        out = subprocess.run(["timedatectl", "list-timezones"], capture_output=True, text=True, timeout=10)
        zones = [z.strip() for z in out.stdout.splitlines() if z.strip()]
        return zones[:limit] if limit else zones
    except FileNotFoundError:
        return ["UTC"]
