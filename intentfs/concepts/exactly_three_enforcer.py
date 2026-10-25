"""The exactly-three guarantee: bounded retry → honest failure."""
from __future__ import annotations

MAX_ATTEMPTS = 3


def enforce(generator, *args, **kwargs) -> dict:
    """generator() -> list[str] | None. Never fabricates; failure stays visible."""
    for attempt in range(MAX_ATTEMPTS):
        result = generator(*args, **kwargs)
        if result is not None:
            return {"index_status": "ready", "concepts": result, "failure_reason": None,
                    "attempts": attempt + 1}
    return {"index_status": "failed", "concepts": None,
            "failure_reason": "could not produce exactly three distinct concepts", "attempts": MAX_ATTEMPTS}
