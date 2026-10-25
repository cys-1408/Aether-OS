"""Reminders client (real service calls)."""
from __future__ import annotations


def add_reminder(app, title: str, due_iso: str) -> dict | None:
    return app.services.call("reminders", "Reminders.add", {"title": title, "due_iso": due_iso})


def list_reminders(app) -> list[dict]:
    result = app.services.call("reminders", "Reminders.list", {})
    return result.get("reminders", []) if result else []
