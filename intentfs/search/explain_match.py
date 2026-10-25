"""Explainable reasons per result (see search_service)."""
from __future__ import annotations


def explain(result: dict) -> list[str]:
    return result.get("reasons", [])
