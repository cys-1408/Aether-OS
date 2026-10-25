"""Normalize raw events into job descriptors."""
from __future__ import annotations


def normalize(kind: str, path: str) -> dict:
    return {"kind": kind, "path": path, "attempts": 0}
