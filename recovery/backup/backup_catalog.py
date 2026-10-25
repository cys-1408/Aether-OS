"""Catalog existing backups found on mounted media (real scan)."""
from __future__ import annotations

import json
from pathlib import Path


def scan(mount: str) -> list[dict]:
    found = []
    for mf in Path(mount).rglob("*.manifest.json"):
        try:
            manifest = json.loads(mf.read_text())
            if manifest.get("type") == "aether-backup-1":
                found.append({"manifest": str(mf),
                              "backup": str(mf.with_suffix("").with_suffix("")),
                              "files": len(manifest.get("files", [])),
                              "created_at": manifest.get("created_at")})
        except json.JSONDecodeError:
            continue
    return found
