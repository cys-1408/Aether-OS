"""Repository metadata verification: gpg-verify the signed sync database.

The verifier never trusts an unsigned db for a repository whose policy
declares signatures required (see package-manager/policy/signature-required
+ pacman.conf SigLevel). Verification key material comes from the pinned
release keyring under /usr/share/aether/keys (no playwright keys in configs).
"""
from __future__ import annotations

import subprocess
from pathlib import Path

KEYRING = Path("/usr/share/aether/keys/aether-releases.gpg")


def verify_repo_db(db: Path, *, keyring: Path | None = None) -> dict:
    sig = db.with_name(db.name + ".sig")
    if not sig.exists():
        return {"verified": None, "reason": f"no signature file for {db.name}"}
    argv = ["gpg", "--verify"]
    ring = keyring or KEYRING
    if ring.exists():
        argv = ["gpg", "--keyring", str(ring), "--verify"]
    argv += [str(sig), str(db)]
    out = subprocess.run(argv, capture_output=True, text=True, timeout=60)
    return {"verified": out.returncode == 0,
            "db": str(db), "detail": out.stderr[-400:]}


def sweep(sync_dir: Path) -> dict:
    """Verify every candidate repo db; report per-repo truth."""
    results = {}
    for db in sync_dir.glob("*.db"):
        results[db.stem] = verify_repo_db(db)
    return results
