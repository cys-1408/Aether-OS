"""Escalation ladder: pause indexing → shrink context → unload idle model."""
from __future__ import annotations

LADDER = ["pause_indexing", "reduce_context", "unload_idle_model", "notify_user"]


def escalation_for(psi: float) -> list[str]:
    if psi is None or psi < 40:
        return []
    if psi < 60:
        return ["pause_indexing"]
    if psi < 80:
        return ["pause_indexing", "reduce_context"]
    return LADDER
