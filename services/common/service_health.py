"""Service registry file handling under /run/aether/."""
from __future__ import annotations

import json
from pathlib import Path
from aether_core.config import atomic_write_json

RUN = Path("/run/aether")


def publish(name: str, status: dict) -> None:
    RUN.mkdir(parents=True, exist_ok=True)
    atomic_write_json(RUN / f"health-{name}.json", status, mode=0o644)


def read_all() -> dict:
    out = {}
    if not RUN.exists():
        return out
    for p in RUN.glob("health-*.json"):
        try:
            out[p.stem.replace("health-", "")] = json.loads(p.read_text())
        except (json.JSONDecodeError, OSError):
            continue
    return out
