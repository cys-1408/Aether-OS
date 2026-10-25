"""Lifecycle states + graceful close handling."""
from __future__ import annotations

from enum import Enum


class AppState(Enum):
    STARTING = "starting"
    READY = "ready"
    BUSY = "busy"
    CLOSING = "closing"


class Lifecycle:
    def __init__(self, app):
        self.app = app
        self.state = AppState.STARTING
        self._dirty_guard = None

    def ready(self):
        self.state = AppState.READY

    def mark_closing(self):
        self.state = AppState.CLOSING
