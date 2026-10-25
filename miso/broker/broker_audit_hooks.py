"""Ledger writes for every broker decision (redacted)."""
from __future__ import annotations

import json
import time
import uuid

from aether_core import paths

LEDGER_SOCK = paths.system_socket("ledger")


def ledger_entry(payload: dict) -> str:
    entry_id = f"le-{uuid.uuid4().hex[:12]}"
    from sensitive_data_filter import redact_params
    entry = {
        "entry_id": entry_id,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "payload": redact_params(payload.get("request", {})),
        "status": payload.get("status"),
        "result": payload.get("result"),
        "verified": payload.get("verified"),
        "decision": payload.get("decision"),
        "error": payload.get("error"),
    }
    try:
        from aether_core.ipc import call
        call(LEDGER_SOCK, "Ledger.append", {"entry": entry}, timeout=5)
    except Exception:
        pass  # broker still returns; health surface reports ledger state
    return entry_id
