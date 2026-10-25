import sys
from pathlib import Path
_p = Path(__file__).resolve()
sys.path.insert(0, str(_p.parents[2] / 'libraries/libaether-core/python'))
"""Streaming digest compare (delete-on-mismatch helper)."""
from pathlib import Path


def verify_and_cleanup(path: Path, expected: str) -> dict:
    from cryptography.artifact_verification import sha256_file
    actual = sha256_file(path)
    if expected and actual != expected:
        path.unlink(missing_ok=True)
        return {"verified": False, "deleted": True}
    return {"verified": True, "sha256": actual}
