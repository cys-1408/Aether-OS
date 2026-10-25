"""Session logic: delegates to the shell focus controller when reachable."""
from __future__ import annotations

import time


class FocusSession:
    def __init__(self, app):
        self.app = app
        self.remaining: int | None = None
        self.running = False
        self.mode = "idle"
        self._end_at = None

    def start(self, minutes: int) -> dict:
        shell = self.app.services.call("shell", "Shell.start_focus", {"minutes": minutes})
        if shell:
            self.mode = "shell-managed"
            self.running = True
            self.remaining = minutes * 60
            self._end_at = time.time() + minutes * 60
            return {"mode": "shell-managed"}
        # standalone fallback timer (real countdown, local only)
        self.mode = "standalone"
        self.running = True
        self.remaining = minutes * 60
        self._end_at = time.time() + minutes * 60
        return {"mode": "standalone"}

    def reset(self) -> None:
        self.running = False
        self.remaining = None
        self.mode = "idle"
        self.app.services.call("shell", "Shell.end_focus", {})

    def render(self) -> str:
        if self.running and self._end_at:
            self.remaining = max(0, int(self._end_at - time.time()))
            m, s = divmod(self.remaining, 60)
            tag = "" if self.mode == "shell-managed" else " (standalone)"
            return f"{m:02d}:{s:02d}{tag}"
        return "--:--"
