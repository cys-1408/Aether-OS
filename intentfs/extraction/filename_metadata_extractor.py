"""Filename metadata: always available even for unsupported formats."""
from __future__ import annotations


def filename_hints(path) -> list[str]:
    import re
    name = path.stem
    words = re.split(r"[\s_.\-]+", name)
    return [w for w in words if len(w) >= 3][:8]
