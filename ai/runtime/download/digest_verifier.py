"""Streaming sha256 verification against trusted metadata."""
from __future__ import annotations

import hashlib
from pathlib import Path

from aether_core.errors import IpcError


def verify_file(path: Path, expected_sha256: str) -> dict:
    if not expected_sha256:
        return {"verified": False, "reason": "no expected digest available"}
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    actual = h.hexdigest()
    if actual != expected_sha256:
        path.unlink(missing_ok=True)
        raise IpcError("E_DIGEST", f"digest mismatch: expected {expected_sha256[:16]}…, got {actual[:16]}… (file deleted)")
    return {"verified": True, "sha256": actual}
