"""Distraction rules read from shell settings."""
from __future__ import annotations


def rules(app) -> dict:
    state = app.services.call("shell", "Shell.capabilities", {})
    return {"distraction_protection": True, "shell_reachable": bool(state)}
