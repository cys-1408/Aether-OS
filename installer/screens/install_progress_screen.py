"""Progress line printer for CLI mode."""
from __future__ import annotations


def show(step: str, detail: str) -> None:
    print(f"[{step}] {detail}")
