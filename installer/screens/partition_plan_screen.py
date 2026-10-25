"""Partition plan: auto ESP+root (manual mode documented)."""
from __future__ import annotations


def plan_cli(disk: str) -> dict:
    print("Plan: 1GiB ESP + remainder root (ext4, labeled AETHEROS)")
    return {"mode": "auto"}
