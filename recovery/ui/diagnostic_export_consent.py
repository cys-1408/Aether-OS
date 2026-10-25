"""Explicit consent gate for diagnostic export."""
from __future__ import annotations


def ask() -> bool:
    return input("Export redacted diagnostics? [y/N]: ").strip().lower() == "y"
