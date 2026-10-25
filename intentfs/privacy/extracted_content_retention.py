"""Snippet retention: capped, local, deletable."""
from __future__ import annotations

SNIPPET_MAX = 2000


def cap_snippet(text: str) -> str:
    return (text or "")[:SNIPPET_MAX]
