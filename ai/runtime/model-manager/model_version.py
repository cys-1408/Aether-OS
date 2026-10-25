"""Model version helpers (repo revision recorded at install)."""
from __future__ import annotations


def version_key(repo: str, file: str) -> str:
    return f"{repo}@{file}"
