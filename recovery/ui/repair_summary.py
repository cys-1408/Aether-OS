"""Summarize repair actions taken."""
from __future__ import annotations


def summarize(actions: list[dict]) -> str:
    lines = [f"{a.get('action')}: {a.get('result')}" for a in actions]
    return "\n".join(lines) or "no actions yet"
