"""Rollback info from updater history (real journal)."""
from __future__ import annotations


def rollback_info(app) -> str:
    data = app.services.call("updates", "Updates.history", {})
    if not data:
        return "update service unreachable"
    items = data.get("history", [])
    if not items:
        return "no update transactions recorded"
    return "\n".join(f"{i.get('ts', '')}: {i.get('action', '')} → {i.get('result', '')}" for i in items[-8:])
