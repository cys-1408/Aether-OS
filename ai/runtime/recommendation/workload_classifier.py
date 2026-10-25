"""Deterministic task classification from free text."""
from __future__ import annotations

PATTERNS = {
    "code": ("code", "function", "python", "bug", "compile", "script"),
    "summarize": ("summar", "tldr", "brief", "overview", "recap"),
    "assistant": ("help", "explain", "what", "how", "write", "draft"),
}


def classify(text: str) -> str:
    low = (text or "").lower()
    for task, words in PATTERNS.items():
        if task != "assistant" and any(w in low for w in words):
            return task
    return "assistant"
