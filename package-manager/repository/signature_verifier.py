"""Package/repository signature validation against configured trust."""
from __future__ import annotations

import subprocess
from pathlib import Path

KEYRING = Path("/usr/share/aether/keys/aether-releases.gpg")


def verify_package_signature(pkg: Path, sig: Path | None = None,
                             *, keyring: Path | None = None) -> dict:
    sig = sig or pkg.with_name(pkg.name + ".sig")
    if not sig.exists():
        return {"verified": None, "reason": "unsigned package tarball"}
    argv = ["gpg", "--verify"]
    ring = keyring or KEYRING
    if ring.exists():
        argv = ["gpg", "--keyring", str(ring), "--verify"]
    argv += [str(sig), str(pkg)]
    out = subprocess.run(argv, capture_output=True, text=True, timeout=60)
    return {"verified": out.returncode == 0, "package": pkg.name,
            "detail": out.stderr[-400:]}


def keyring_present() -> dict:
    return {"path": str(KEYRING), "present": KEYRING.exists()}
