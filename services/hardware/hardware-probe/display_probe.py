"""Real display facts from /sys/class/drm."""
from __future__ import annotations

from pathlib import Path


def display_facts() -> list[dict]:
    out = []
    for card in sorted(Path("/sys/class/drm").glob("card*-?")):
        name = card.name
        status = None
        try:
            status = (card / "status").read_text().strip()
        except OSError:
            pass
        enabled = None
        try:
            enabled = (card / "enabled").read_text().strip()
        except OSError:
            pass
        modes = []
        try:
            modes_text = (card / "modes").read_text()
            modes = [m.strip() for m in modes_text.splitlines()[:5]]
        except OSError:
            pass
        out.append({"connector": name, "status": status, "enabled": enabled, "modes": modes})
    return out
