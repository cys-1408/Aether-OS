"""Priority helpers for the job queue (user-visible > recent > backlog)."""
from __future__ import annotations


def priority_for(path: str, recently_used: bool) -> int:
    return 2 if recently_used else 5
