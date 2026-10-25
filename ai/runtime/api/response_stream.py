"""Stream chunking for streamed inference replies."""
from __future__ import annotations


def chunks(text: str, size: int = 24):
    for i in range(0, len(text), size):
        yield text[i:i + size]
