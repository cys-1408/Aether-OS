"""Monotonic timers for internal service use."""
from __future__ import annotations

import threading
import time
from typing import Callable


class MonotonicTimer:
    def __init__(self) -> None:
        self._start = time.monotonic()

    def elapsed_s(self) -> float:
        return time.monotonic() - self._start

    def reset(self) -> None:
        self._start = time.monotonic()


def schedule_once(delay_s: float, fn: Callable[[], None]) -> threading.Timer:
    t = threading.Timer(delay_s, fn)
    t.daemon = True
    t.start()
    return t
