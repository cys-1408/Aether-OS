"""Structured account event log lines (journald-friendly)."""
from __future__ import annotations

import json
import time


def log_event(logger, event: str, **fields) -> None:
    record = {"ts": time.strftime("%Y-%m-%dT%H:%M:%S%z"), "event": event, **fields}
    logger.info(json.dumps(record))
