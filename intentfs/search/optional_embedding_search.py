"""Optional embeddings channel (disabled unless configured)."""
from __future__ import annotations


def matches(query: str, field: str | None) -> bool:
    if not field:
        return False
    q = query.lower()
    return q in field.lower()
