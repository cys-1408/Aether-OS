"""Verify last backup (real re-hash on service side)."""
from __future__ import annotations


def verify_last(app) -> str:
    status = app.services.call("backup", "Backup.status", {})
    last = (status or {}).get("last_backup")
    if not last:
        return "no backup to verify"
    result = app.services.call("backup", "Backup.verify", {"file": last}, timeout=600)
    return str(result)
