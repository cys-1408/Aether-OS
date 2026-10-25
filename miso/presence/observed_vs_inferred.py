"""Label observed facts vs inferred interpretations."""
from __future__ import annotations


def message(observed: str, inferred: str | None = None) -> str:
    if inferred:
        return f"observed: {observed} · inferred: {inferred}"
    return f"observed: {observed}"
