"""Migration 001: no-op (v1 baseline)."""
from __future__ import annotations


def apply(doc: dict) -> dict:
    return doc
