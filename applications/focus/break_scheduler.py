"""Break reminders every N focus sessions (real notifications)."""
from __future__ import annotations


class BreakScheduler:
    def __init__(self, app, every: int = 3):
        self.app = app
        self.every = every
        self.count = 0

    def on_session_complete(self) -> None:
        self.count += 1
        if self.count % self.every == 0:
            self.app.services.call("notifications", "Notify.notify",
                                   {"source": "focus", "category": "focus",
                                    "title": "Break time", "body": f"{self.count} sessions done — take a 5 minute break."})
