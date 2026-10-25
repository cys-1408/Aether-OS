"""Deterministic intent classification first; LLM only as refinement."""
from __future__ import annotations

PATTERNS = [
    ("find_file", ("find a file", "find file", "search for", "where is my", "locate")),
    ("open_app", ("open the", "open ", "launch", "start the")),
    ("focus", ("help me focus", "focus for", "start focus", "hide distractions")),
    ("break", ("take a break", "five-minute break", "rest")),
    ("organize", ("organize", "tile", "arrange windows", "tidy")),
    ("status", ("system status", "how is my", "cpu", "memory", "storage", "battery")),
    ("model", ("install a model", "download model", "switch model", "which model")),
    ("workspace", ("save workspace", "save my layout", "restore workspace")),
]


def classify(text: str) -> tuple[str, float]:
    low = (text or "").lower().strip()
    for intent, words in PATTERNS:
        if any(w in low for w in words):
            return intent, 0.9
    return "unknown", 0.3
