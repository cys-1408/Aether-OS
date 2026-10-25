"""Re-hash installed model files before load."""
from __future__ import annotations

import hashlib
from pathlib import Path

from aether_core.errors import AetherError


def verify_model_file(path: Path, expected_sha256: str) -> dict:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    actual = h.hexdigest()
    if expected_sha256 and actual != expected_sha256:
        raise AetherError("E_MODEL_DIGEST", f"model file corrupted: {path.name}")
    return {"verified": True, "sha256": actual}
