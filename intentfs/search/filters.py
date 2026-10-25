"""Search filters: type/date/location/size/index-status."""
from __future__ import annotations


def apply(results: list[dict], filters: dict) -> list[dict]:
    out = results
    if ftype := filters.get("type"):
        out = [r for r in out if (r.get("record", {}).get("mime_type") or "").startswith(ftype)]
    if status := filters.get("index_status"):
        out = [r for r in out if r.get("index_status") == status]
    if loc := filters.get("location"):
        out = [r for r in out if loc in (r.get("path") or "")]
    return out
