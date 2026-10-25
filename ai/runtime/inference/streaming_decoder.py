"""Streaming decode helper (chunked delivery)."""
from __future__ import annotations


def stream(text: str, chunk_size: int = 32):
    for i in range(0, len(text), chunk_size):
        yield text[i:i + chunk_size]
