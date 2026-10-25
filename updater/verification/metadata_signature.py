"""Verify signed update/repo metadata before trusting package listings."""
from __future__ import annotations

import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from metadata_verifier import verify_repo, verify_manifest  # noqa: E402

TRUST_ROOT = Path("/etc/aether/trusted-keys")  # armored release keys


def verify(repo_db: Path) -> dict:
    """gpg-verify the repo db against the trusted update-policy keyring..."""
    keyring = TRUST_ROOT / "aether-updates.gpg"
    argv = ["gpg", "--verify"]
    if keyring.exists():
        argv = ["gpg", "--keyring", str(keyring), "--verify"]
    sig = repo_db.with_suffix(repo_db.suffix + ".sig")
    if not sig.exists():
        return {"verified": None,
                "reason": "metadata unsigned; update proceeds only from "
                          "signed media per rootfs/etc/aether/update-policy.yaml"}
    argv += [str(sig), str(repo_db)]
    out = subprocess.run(argv, capture_output=True, text=True, timeout=60)
    return {"verified": out.returncode == 0, "detail": out.stderr[-400:]}


def verify_release_manifest(manifest: Path, artifacts: list[Path]) -> dict:
    return verify_manifest(manifest, artifacts)


__all__ = ["verify_repo", "verify_manifest", "verify", "verify_release_manifest"]
