"""Display/connector discovery."""
from __future__ import annotations

from pathlib import Path


def discover() -> list[dict]:
    out = []
    for card in sorted(Path("/sys/class/drm").glob("card*-?")):
        try:
            out.append({"connector": card.name,
                        "status": (card / "status").read_text().strip()})
        except OSError:
            continue
    return out
