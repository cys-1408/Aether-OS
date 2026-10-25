"""Freshness decay (30-day half-life-ish)."""
from __future__ import annotations

import datetime


def boost(indexed_at: str | None) -> float:
    if not indexed_at:
        return 0.5
    try:
        t = datetime.datetime.fromisoformat(indexed_at[:19])
        age_days = max(0.0, (datetime.datetime.now() - t).total_seconds() / 86400)
        return 1.0 / (1.0 + age_days / 30.0)
    except Exception:
        return 0.5
