import sys
from pathlib import Path
_p = Path(__file__).resolve()
sys.path.insert(0, str(_p.parents[2] / 'libraries/libaether-core/python'))
"""Artifact verification: sha256 + optional GPG (used by runtime/updater)."""
import hashlib
import subprocess
from pathlib import Path


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def gpg_verify(signature: Path, target: Path) -> dict:
    try:
        out = subprocess.run(["gpg", "--verify", str(signature), str(target)],
                             capture_output=True, text=True, timeout=30)
        return {"verified": out.returncode == 0, "detail": out.stderr[-200:]}
    except FileNotFoundError:
        return {"verified": None, "reason": "gpg not installed"}
