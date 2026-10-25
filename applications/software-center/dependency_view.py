"""Dependency display via pacman -Si depends (real data)."""
from repository_browser import package_details  # noqa: F401


def depends(name: str) -> list[str]:
    raw = package_details(name).get("Depends On", "")
    return [d for d in raw.replace("None", "").split() if d]
