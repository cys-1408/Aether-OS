"""Virtual desktops = sway workspaces."""
from __future__ import annotations

from aether_core.swayipc import SwayIPC


def workspaces() -> list[dict]:
    try:
        return SwayIPC().get_workspaces()
    except (ConnectionError, OSError):
        return []


def switch(name: str) -> dict:
    from compositor_adapter import CompositorAdapter
    return CompositorAdapter().run(f"workspace {name}")


def create(name: str) -> dict:
    return switch(name)
