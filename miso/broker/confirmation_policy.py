"""Confirmation requirements resolution."""
from __future__ import annotations


def required(cap: dict, decision: str) -> str:
    if cap.get("confirmation") == "always":
        return "always"
    if decision == "confirm":
        return "policy"
    return "never"
