"""Command search: apps + registered actions ONLY (never model output)."""
from __future__ import annotations

from app_catalog import build_catalog


def search(query: str, limit: int = 12) -> list[dict]:
    q = query.strip().lower()
    if not q:
        return build_catalog()[:limit]
    scored = []
    for item in build_catalog():
        name = item["name"].lower()
        if q in name:
            scored.append((0 if name.startswith(q) else 1, item))
    scored.sort(key=lambda pair: pair[0])
    return [i for _, i in scored[:limit]]
