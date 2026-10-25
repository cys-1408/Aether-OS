"""Real focus sessions: sway dimming, timer, pause/end, completion notify."""
from __future__ import annotations

import time

from aether_core.config import atomic_write_json
from aether_core import paths

SESSIONS_FILE = paths.USER_STATE_DIR / "focus-sessions.json"


class FocusController:
    def __init__(self, wm, shell=None):
        self.wm = wm
        self.shell = shell
        self.active = False
        self.paused = False
        self.remaining: int | None = None
        self._target_app = None
        self._started_at = None
        self._minutes = 25
        self._tick_source = None
        from gi.repository import GLib
        self._GLib = GLib

    def start(self, minutes: int = 25, target_app: str | None = None) -> dict:
        if self.active:
            self.end()
        self.active = True
        self.paused = False
        self._minutes = minutes
        self.remaining = minutes * 60
        self._started_at = time.time()
        self._target_app = target_app
        # Dim every window except the target (real sway opacity)
        for win in self.wm.windows():
            wid = win["id"]
            if target_app and target_app in (win.get("app_id") or ""):
                self.wm.set_opacity(wid, 1.0)
            else:
                self.wm.set_opacity(wid, 0.15)
        self._tick_source = self._GLib.timeout_add_seconds(1, self._tick)
        self._record("started")
        if self.shell:
            self.shell.controller.on_focus_state(True, self.remaining)
        return {"started": True, "minutes": minutes}

    def pause(self) -> dict:
        if not self.active:
            return {"error": "no active session"}
        self.paused = not self.paused
        self._record("paused" if self.paused else "resumed")
        return {"paused": self.paused}

    def end(self, completed: bool = False) -> dict:
        if self._tick_source:
            self._GLib.source_remove(self._tick_source)
            self._tick_source = None
        for win in self.wm.windows():
            self.wm.set_opacity(win["id"], 1.0)
        if self.active:
            self._record("completed" if completed else "ended")
        was = self.active
        self.active = False
        self.paused = False
        self.remaining = None
        if self.shell and was:
            self.shell.controller.on_focus_state(False, None)
        return {"ended": True, "completed": completed}

    def _tick(self):
        if not self.active or self.paused:
            return True
        self.remaining = (self.remaining or 0) - 1
        if self.shell:
            self.shell.controller.on_focus_state(True, self.remaining)
        if self.remaining is not None and self.remaining <= 0:
            self.end(completed=True)
            self._notify_completion()
            return False
        return True

    def _notify_completion(self):
        try:
            from service_kit import call_service  # type: ignore
        except ImportError:
            pass
        import sys
        from pathlib import Path
        sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "libraries/libaether-core/python"))
        from aether_core.ipc import call
        from aether_core import paths as _paths
        try:
            call(_paths.system_socket("notifications"), "Notify.notify",
                 {"source": "focus", "category": "focus", "title": "Focus session completed",
                  "body": f"Nice work — {self._minutes} minutes of focus."}, timeout=4)
        except Exception:
            pass

    def _record(self, event: str) -> None:
        try:
            sessions = []
            if SESSIONS_FILE.exists():
                import json
                sessions = json.loads(SESSIONS_FILE.read_text())
            sessions.append({"event": event, "at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
                             "minutes": self._minutes})
            atomic_write_json(SESSIONS_FILE, sessions[-50:])
        except Exception:
            pass
