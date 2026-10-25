"""Preview restore conflicts (real file comparisons)."""
from __future__ import annotations

import json
from pathlib import Path


def preview(manifest_path: str) -> dict:
    manifest = json.loads(Path(manifest_path).read_text())
    conflicts = 0
    for entry in manifest.get("files", []):
        if (Path("/mnt/recovery-target") / entry["path"]).exists():
            conflicts += 1
    return {"files": len(manifest.get("files", [])), "conflicts": conflicts}
