"""Graceful shutdown orchestration: run cleanup callbacks on SIGTERM."""
from __future__ import annotations

import signal
from typing import Callable


class ShutdownHandler:
    def __init__(self) -> None:
        self._callbacks: list[Callable[[], None]] = []

    def register(self, cb: Callable[[], None]) -> None:
        self._callbacks.append(cb)

    def install(self) -> None:
        signal.signal(signal.SIGTERM, self._run_all)
        signal.signal(signal.SIGINT, self._run_all)

    def _run_all(self, signum, frame) -> None:
        for cb in self._callbacks:
            try:
                cb()
            except Exception:
                pass
