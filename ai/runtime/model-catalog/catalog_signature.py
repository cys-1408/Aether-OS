"""Catalog authenticity: sha256 digest (required) + optional GPG (when present)."""
from __future__ import annotations

import subprocess
from pathlib import Path

import hashlib


def verify_digest(catalog_path: Path) -> dict:
    digest_file = catalog_path.with_suffix(catalog_path.suffix + ".sha256")
    if not digest_file.exists():
        return {"verified": False, "reason": "digest file missing — run repo tooling to generate"}
    recorded = digest_file.read_text().split()[0]
    actual = hashlib.sha256(catalog_path.read_bytes()).hexdigest()
    return {"verified": recorded == actual, "recorded": recorded, "actual": actual}


def verify_gpg(catalog_path: Path) -> dict:
    sig = catalog_path.with_suffix(catalog_path.suffix + ".sig")
    if not sig.exists():
        return {"verified": None, "reason": "no GPG signature shipped (digest covers integrity)"}
    try:
        out = subprocess.run(["gpg", "--verify", str(sig), str(catalog_path)],
                             capture_output=True, text=True, timeout=20)
        return {"verified": out.returncode == 0, "detail": out.stderr.strip()[-200:]}
    except FileNotFoundError:
        return {"verified": None, "reason": "gpg not installed"}
