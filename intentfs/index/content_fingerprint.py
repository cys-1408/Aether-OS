"""Content sha256 fingerprint."""
from __future__ import annotations

import hashlib
from pathlib import Path


def sha256_of(path: Path) -> str | None:
    try:
        h = hashlib.sha256()
        with open(path, "rb") as fh:
            for chunk in iter(lambda: fh.read(1 << 18), b""):
                h.update(chunk)
        return h.hexdigest()
    except OSError:
        return None
