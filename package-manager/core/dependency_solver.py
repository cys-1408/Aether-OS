"""Dependency resolution preview via pacman -Si."""
from __future__ import annotations

from package_manager import info


def install_set(packages: list[str]) -> dict:
    deps = []
    for p in packages:
        raw = info(p).get("Depends On", "")
        deps.extend(d for d in raw.replace("None", "").split() if d)
    return {"explicit": packages, "dependencies": sorted(set(deps))}
