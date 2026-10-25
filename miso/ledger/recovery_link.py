"""Link ledger entries to rollback options."""
from __future__ import annotations


def recovery_link(entry: dict) -> dict:
    payload = entry.get("request", {}).get("payload", entry.get("request", {}))
    undo = payload.get("_undo") or {}
    return {"entry_id": entry.get("entry_id"),
            "rollback_available": bool(undo),
            "rollback": undo or None}
