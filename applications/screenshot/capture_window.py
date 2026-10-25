"""Window capture helper (see screenshot_service.capture('window'))."""
from screenshot_service import capture  # noqa: F401


def capture_window() -> dict:
    return capture("window")
