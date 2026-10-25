"""Verify repo signature + release manifest digests."""
from __future__ import annotations

import hashlib
import subprocess
from pathlib import Path


def verify_repo(db_path: Path) -> dict:
    sig = db_path.with_suffix(db_path.suffix + ".sig")
    if not sig.exists():
        return {"verified": None, "reason": "repo db unsigned (local media repo)"}
    out = subprocess.run(["gpg", "--verify", str(sig), str(db_path)],
                         capture_output=True, text=True, timeout=30)
    return {"verified": out.returncode == 0, "detail": out.stderr[-200:]}


def verify_manifest(manifest: Path, artifacts: list[Path]) -> dict:
    import json
    data = json.loads(manifest.read_text())
    for art in data.get("artifacts", []):
        local = next((a for a in artifacts if a.name == art["name"]), None)
        if local and hashlib.sha256(local.read_bytes()).hexdigest() != art["sha256"]:
            return {"verified": False, "mismatch": art["name"]}
    return {"verified": True}
