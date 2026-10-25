"""Restore with preview + explicit conflict decisions (no silent overwrite)."""
from __future__ import annotations

import json
import tarfile
from pathlib import Path


def preview(backup_path: str) -> dict:
    path = Path(backup_path)
    mpath = path.parent / (path.name + ".manifest.json")
    if not mpath.exists():
        return {"ok": False, "reason": "manifest missing"}
    manifest = json.loads(mpath.read_text())
    conflicts, restorable = [], 0
    for entry in manifest["files"]:
        target = Path("/") / entry["path"]
        if target.exists():
            try:
                existing = target.read_bytes()
                conflicts.append({"path": entry["path"], "existing_size": len(existing),
                                  "backup_size": entry["size"]})
            except OSError:
                conflicts.append({"path": entry["path"], "existing_size": None,
                                  "backup_size": entry["size"]})
        else:
            restorable += 1
    return {"ok": True, "restorable": restorable, "conflicts": conflicts[:100],
            "policies": ["fail", "rename", "overwrite-with-confirm"]}


def restore(backup_path: str, *, conflict_policy: str = "fail",
            confirm_overwrite: bool = False) -> dict:
    if conflict_policy == "overwrite" and not confirm_overwrite:
        return {"ok": False, "reason": "overwrite requires confirm_overwrite=true"}
    path = Path(backup_path)
    restored, skipped, renamed = 0, 0, 0
    try:
        with tarfile.open(path, "r:gz") as tar:
            for member in tar.getmembers():
                if not member.isfile():
                    continue
                target = Path("/") / member.name
                if not str(target).startswith(("/home/", str(Path.home()))):
                    skipped += 1
                    continue  # refuse to restore outside user areas
                if target.exists():
                    if conflict_policy == "fail":
                        return {"ok": False, "reason": f"conflict at {target}; use preview + policy"}
                    if conflict_policy == "rename":
                        i = 2
                        while target.with_name(f"{target.name} ({i})").exists():
                            i += 1
                        target = target.with_name(f"{target.name} ({i})")
                        renamed += 1
                    elif conflict_policy == "overwrite" and confirm_overwrite:
                        pass
                target.parent.mkdir(parents=True, exist_ok=True)
                src = tar.extractfile(member)
                target.write_bytes(src.read())
                restored += 1
    except (tarfile.TarError, OSError) as e:
        return {"ok": False, "reason": str(e)}
    return {"ok": True, "restored": restored, "skipped": skipped, "renamed": renamed}
