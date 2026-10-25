"""Decompose compound intents into ordered sub-plans."""
from __future__ import annotations


def decompose(text: str) -> list[str]:
    """Split on ' and then ' / ' then ' for simple sequencing."""
    import re
    parts = re.split(r"\s+(?:and then|then)\s+", text.strip(), flags=re.I)
    return [p.strip() for p in parts if p.strip()]
