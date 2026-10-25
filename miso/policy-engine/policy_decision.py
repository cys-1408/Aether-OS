"""Decision record shape."""
from __future__ import annotations


def record(decision: str, reasons: list, applied: str) -> dict:
    return {"decision": decision, "reasons": reasons, "applied_policy": applied}
