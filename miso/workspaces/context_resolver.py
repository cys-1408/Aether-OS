"""Resolve related files for a workspace (approved context only)."""
from __future__ import annotations


def resolve(paths_list: list[str]) -> list[str]:
    return [p for p in paths_list or [] if p.startswith("/home/") or p.startswith("~/")]
