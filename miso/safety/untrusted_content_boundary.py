"""Untrusted content framing: file/text content is DATA, never instructions."""
from __future__ import annotations


def wrap_untrusted(content: str) -> str:
    return f"<untrusted-data>\n{content[:8000]}\n</untrusted-data>"
