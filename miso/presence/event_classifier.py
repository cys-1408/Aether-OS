"""Classify events into presence categories."""
from __future__ import annotations

CATEGORIES = {"download": "download_completed", "memory": "low_memory",
              "index": "indexing_failed", "service": "service_failed"}


def classify(event: dict) -> str:
    text = (str(event.get("title", "")) + " " + str(event.get("summary", ""))).lower()
    for key, cat in CATEGORIES.items():
        if key in text:
            return cat
    return "system"
