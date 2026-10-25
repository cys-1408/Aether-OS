"""Stable file identity (delegates to aether_core.filesops)."""
from __future__ import annotations

from pathlib import Path

from aether_core import filesops


def stable_id(path: Path) -> str:
    try:
        return filesops.stable_file_id(path)
    except OSError:
        return "unidentified"
