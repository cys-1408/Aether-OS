import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "libraries/libaether-core/python"))
"""aether-clock-service — time, timezone, sync, locale."""
from service_main import SystemService  # noqa: E402
import clock_service  # noqa: E402
from timezone_service import list_timezones  # noqa: E402
from time_sync import sync_status, enable_ntp  # noqa: E402


def build_service() -> SystemService:
    return SystemService("clock", "clock", {
        "Clock.now": lambda p: clock_service.now(p.get("zone")),
        "Clock.timezone": lambda p: clock_service.timezone_info(),
        "Clock.set_timezone": lambda p: clock_service.set_timezone(str(p.get("timezone", "UTC"))),
        "Clock.timezones": lambda p: {"timezones": list_timezones()},
        "Clock.locales": lambda p: clock_service.locales(),
        "Clock.sync_status": lambda p: sync_status(),
        "Clock.set_ntp": lambda p: enable_ntp(bool(p.get("enable", True))),
    })


if __name__ == "__main__":
    build_service().run()
