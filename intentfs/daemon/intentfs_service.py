"""IntentFS service core: per-user indexes, jobs, search façade."""
from __future__ import annotations

import threading
import time

from aether_core import paths


class IntentFSService:
    def __init__(self, config: dict):
        self.config = config
        self.paused = False
        self._lock = threading.Lock()
        self.stats = {"indexed": 0, "failed": 0, "pending": 0, "started_at": time.strftime("%Y-%m-%dT%H:%M:%S%z")}

    def status(self) -> dict:
        return {"service": "intentfs", "paused": self.paused, "stats": dict(self.stats),
                "watch_roots": self.config.get("watch_roots", []),
                "note": "original files are never modified by indexing"}

    def set_paused(self, paused: bool) -> dict:
        self.paused = bool(paused)
        return {"paused": self.paused}
