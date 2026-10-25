"""Apply restore with per-file decisions."""
from __future__ import annotations

import json
import tarfile
from pathlib import Path


def restore(backup_path: str, root: str, policy: str = "rename") -> dict:
    restored = 0
    with tarfile.open(backup_path, "r:gz") as tar:
        for member in tar.getmembers():
            if not member.isfile():
                continue
            target = Path(root) / member.name
            if target.exists() and policy == "fail":
                return {"restored": restored, "stopped_at": member.name}
            if target.exists() and policy == "rename":
                i = 2
                while target.with_name(f"{target.name} ({i})").exists():
                    i += 1
                target = target.with_name(f"{target.name} ({i})")
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(tar.extractfile(member).read())
            restored += 1
    return {"restored": restored}
