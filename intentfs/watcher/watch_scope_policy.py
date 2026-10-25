"""What to watch: roots, exclusions, sensitive paths, size caps."""
from __future__ import annotations

from pathlib import Path


def in_scope(path: Path, config: dict) -> bool:
    from folder_exclusions import excluded
    if excluded(str(path), config):
        return False
    max_mb = int(config.get("max_file_size_mb", 20))
    try:
        if path.is_file() and path.stat().st_size > max_mb * 1024 * 1024:
            return False
    except OSError:
        return False
    return True
