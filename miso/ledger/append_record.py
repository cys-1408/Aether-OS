"""Append record validation against the ledger schema."""
from __future__ import annotations

from aether_core.errors import IpcError


def validate_entry(entry: dict) -> None:
    required = {"entry_id", "timestamp", "payload", "status"}
    missing = required - set(entry)
    if missing:
        raise IpcError("E_INVALID", f"ledger entry missing: {sorted(missing)}")
