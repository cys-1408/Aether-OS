"""Exactly-the-three-concepts chip renderer with truthful states."""
from __future__ import annotations


def chip_text(record: dict | None) -> str:
    if not record:
        return "no index record"
    status = record.get("index_status")
    if status == "ready":
        return " · ".join(record.get("concepts", []))
    if status == "pending":
        return "indexing pending" + (f" — {record.get('failure_reason')}" if record.get("failure_reason") else "")
    if status == "pending-limited":
        return "metadata only (format unsupported for full indexing)"
    if status == "failed":
        return f"indexing failed — {record.get('failure_reason', 'unknown reason')}"
    if status == "excluded":
        return "excluded by privacy policy"
    return status or "unknown index state"
