"""Completion notification (dedup with the shell's own)."""
from __future__ import annotations


def notify(app, minutes: int, mode: str) -> None:
    if mode == "shell-managed":
        return  # the shell focus controller already notifies
    app.services.call("notifications", "Notify.notify",
                      {"source": "focus", "category": "focus",
                       "title": "Focus session completed",
                       "body": f"{minutes} minutes — nice work."})
