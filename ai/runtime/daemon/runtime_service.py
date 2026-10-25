"""Runtime service core: state machine + model lifecycle + inference routing."""
from __future__ import annotations

import threading
import time

from aether_core.config import atomic_write_json
from aether_core.errors import IpcError
from aether_core import paths

STATE_FILE = paths.SYSTEM_STATE_DIR / "runtime" / "state.json"

VALID_STATES = ("not_configured", "profiling", "recommendation_ready", "awaiting_consent",
                "downloading", "installing", "validating", "ready", "degraded")


class RuntimeService:
    def __init__(self, config: dict):
        self.config = config
        self.state = "not_configured"
        self.reason: str | None = None
        self._lock = threading.Lock()
        self.backend = None          # set by the backend adapter
        self.profile = {}
        self._downloads: dict[str, dict] = {}
        self._load_state()

    # ------------------------------------------------------------ state
    def set_state(self, state: str, reason: str | None = None) -> None:
        if state not in VALID_STATES:
            raise IpcError("E_INVALID", f"unknown state {state}")
        with self._lock:
            self.state = state
            self.reason = reason
        self._save_state()

    def _load_state(self) -> None:
        try:
            data = json.loads(STATE_FILE.read_text())
            self.state = data.get("state", "not_configured")
            self.reason = data.get("reason")
        except (OSError, json.JSONDecodeError):
            pass

    def _save_state(self) -> None:
        try:
            atomic_write_json(STATE_FILE, {"state": self.state, "reason": self.reason,
                                           "updated_at": time.strftime("%Y-%m-%dT%H:%M:%S%z")})
        except OSError:
            pass

    # ------------------------------------------------------------ status
    def status(self) -> dict:
        out = {"state": self.state, "reason": self.reason, "local_only": True}
        if self.backend:
            out["backend"] = self.backend.describe()
        return out
