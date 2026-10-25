"""Language/keyboard choice (delegates to localectl)."""
from __future__ import annotations


def choices_cli() -> dict:
    locale = input("Locale [en_US.UTF-8]: ").strip() or "en_US.UTF-8"
    layout = input("Keyboard layout [us]: ").strip() or "us"
    return {"locale": locale, "keyboard": layout}
