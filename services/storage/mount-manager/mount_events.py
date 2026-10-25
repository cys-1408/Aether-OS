"""Mount event journaling (structured, redacted)."""
from __future__ import annotations

import time

from aether_core.logging_setup import configure_logging

log = configure_logging("mount-events")


def record(event: str, device: str, mountpoint: str | None = None, **extra) -> None:
    record = {"ts": time.strftime("%Y-%m-%dT%H:%M:%S%z"), "event": event,
              "device": device, "mountpoint": mountpoint, **extra}
    log.info(str(record))
