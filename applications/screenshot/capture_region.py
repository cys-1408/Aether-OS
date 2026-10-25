"""Region capture helper (see screenshot_service.capture('region'))."""
from screenshot_service import capture  # noqa: F401


def capture_region() -> dict:
    return capture("region")
