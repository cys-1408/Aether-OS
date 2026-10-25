"""ATK descriptions for the companion (screen readers)."""
from __future__ import annotations


def describe(state: str) -> str:
    from miso_status_indicator import label_for
    return f"Miso, the desktop assistant cat. Current state: {label_for(state)}."
