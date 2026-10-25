"""Verify the digest of every staged package before activation."""
from __future__ import annotations

import hashlib
from pathlib import Path


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def verify_staged(cache_dir: Path, metadata: dict) -> dict:
    """Compare each staged archive with its trusted digest.

    metadata: {"packages": [{"name":..., "digest":..., "filename":...}]}
    Mismatching or missing digests are reported truthfully and block apply.
    """
    results = []
    ok = True
    for entry in metadata.get("packages", []):
        fname = entry.get("filename") or f"{entry['name']}.pkg.tar.zst"
        local = cache_dir / fname
        if not local.exists():
            ok = False
            results.append({"name": entry["name"], "status": "missing"})
            continue
        if not entry.get("digest"):
            ok = False
            results.append({"name": entry["name"], "status": "no-trusted-digest"})
            continue
        actual = _sha256(local)
        status = "verified" if actual == entry["digest"] else "mismatch"
        if status != "verified":
            ok = False
        results.append({"name": entry["name"], "status": status})
    return {"ok": ok, "packages": results}


def verify_one(package_path: Path, expected_digest: str) -> dict:
    actual = _sha256(package_path)
    return {"name": package_path.name, "status":
            "verified" if actual == expected_digest else "mismatch"}
