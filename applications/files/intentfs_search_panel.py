"""Search panel logic shared by Files (kept importable for tests)."""
from __future__ import annotations


def normalize_results(data: dict | None, fallback_fn) -> tuple[list[dict], str]:
    if data and data.get("results") is not None:
        return data["results"], "IntentFS semantic results"
    return fallback_fn(), "IntentFS unavailable — filename search only"
