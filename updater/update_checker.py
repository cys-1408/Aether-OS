"""Compare installed vs repo versions (real pacman queries)."""
from __future__ import annotations

import subprocess


def check() -> dict:
    try:
        sync = subprocess.run(["pacman", "-Sup", "--print-format", "%n %v"],
                              capture_output=True, text=True, timeout=300)
        updates = [l.split() for l in sync.stdout.splitlines() if l.strip()]
        return {"status": "updates-available" if updates else "up-to-date",
                "summary": f"{len(updates)} package(s)", "updates": updates[:50]}
    except FileNotFoundError:
        return {"status": "unavailable", "summary": "pacman not installed"}
