"""Policy tamper detection → fail closed."""
from __future__ import annotations

import hashlib
from pathlib import Path


def file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.exists() else ""


def verify_hashes(hashes: dict[str, str]) -> bool:
    for name, expected in hashes.items():
        if expected and file_hash(Path(name)) != expected:
            return False
    return True
