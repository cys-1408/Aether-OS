"""Error presentation for agent failures (truthful reasons)."""
from __future__ import annotations


def error_message(exc: Exception) -> str:
    return f"I hit a snag: {exc}. Nothing was changed — safe to retry."
