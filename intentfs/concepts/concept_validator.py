"""Exactly-three distinct valid concepts."""
from __future__ import annotations


def valid(concepts: list[str]) -> bool:
    if len(concepts) != 3:
        return False
    if len(set(concepts)) != 3:
        return False
    return all(2 <= len(c) <= 32 for c in concepts)
