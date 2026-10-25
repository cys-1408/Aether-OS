"""Network choice (optional; offline install supported)."""
from __future__ import annotations


def choices_cli() -> dict:
    use = input("Enable networking? [Y/n]: ").strip().lower() != "n"
    return {"networking": use}
