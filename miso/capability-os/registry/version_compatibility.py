"""Semver-ish compatibility check."""
from __future__ import annotations


def compatible(required: str, provided: str) -> bool:
    try:
        r = [int(x) for x in required.split(".")[:2]]
        p = [int(x) for x in provided.split(".")[:2]]
    except (ValueError, IndexError):
        return False
    return r[0] == p[0] and p[1] >= r[1]
