"""Uniqueness check (case-insensitive distinct)."""
from __future__ import annotations


def all_unique(concepts: list[str]) -> bool:
    lowered = [c.lower() for c in concepts]
    return len(lowered) == len(set(lowered))
