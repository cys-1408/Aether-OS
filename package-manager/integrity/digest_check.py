"""Package file digest verification (sha256 of the archive)."""
from __future__ import annotations

import hashlib
from pathlib import Path


def digest(pkg_path: Path) -> str:
    h = hashlib.sha256()
    with open(pkg_path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()
