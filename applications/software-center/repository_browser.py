"""Real pacman repo queries."""
from __future__ import annotations

import subprocess


def search_packages(query: str) -> list[dict]:
    try:
        out = subprocess.run(["pacman", "-Sl"], capture_output=True, text=True, timeout=30)
        pkgs = []
        for line in out.stdout.splitlines():
            parts = line.split()
            if len(parts) >= 3 and (not query or query.lower() in parts[1].lower()):
                pkgs.append({"repo": parts[0], "name": parts[1], "version": parts[2]})
        return pkgs
    except FileNotFoundError:
        return []


def installed_names() -> set[str]:
    try:
        out = subprocess.run(["pacman", "-Qq"], capture_output=True, text=True, timeout=30)
        return set(out.stdout.split())
    except FileNotFoundError:
        return set()


def package_details(name: str) -> dict:
    out = subprocess.run(["pacman", "-Si", name], capture_output=True, text=True, timeout=15)
    details = {}
    for line in out.stdout.splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            details[k.strip()] = v.strip()
    return details
