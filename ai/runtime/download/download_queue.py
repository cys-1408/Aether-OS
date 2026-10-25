"""Download queue with bounded concurrency (1 active)."""
from __future__ import annotations

import queue
import threading

_q: queue.Queue = queue.Queue()
_active = threading.Semaphore(1)


def enqueue(fn) -> None:
    def run():
        with _active:
            fn()
    threading.Thread(target=run, daemon=True).start()
