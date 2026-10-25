"""Privacy defaults recap (local-first; toggles mirror first-boot)."""
from __future__ import annotations


def choices_cli() -> dict:
    clip = input("Clipboard history? [y/N]: ").strip().lower() == "y"
    return {"clipboard_history": clip}
