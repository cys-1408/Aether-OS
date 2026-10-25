"""Failure path messaging."""
from __future__ import annotations


def failed(step: str, reason: str) -> None:
    print(f"Installation FAILED at {step}: {reason}")
    print("The partition-table backup enables rollback; see recovery/install_rollback.py")
