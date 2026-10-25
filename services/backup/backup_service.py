"""Manifest-based backup with per-file sha256 + verify; user-scoped."""
from __future__ import annotations

import gzip
import hashlib
import io
import json
import os
import tarfile
import time
from pathlib import Path

from aether_core import paths
from aether_core.config import load_yaml
from aether_core.errors import AetherError

USER_CONFIG = paths.USER_CONFIG_DIR / "backup.yaml"
STATE = paths.USER_STATE_DIR / "backup-state.json"


def targets() -> dict:
    cfg = load_yaml(USER_CONFIG)
    return {"configured": bool(cfg), "targets": cfg.get("targets", []),
            "includes": cfg.get("includes", [str(Path.home() / "Documents")])}


def run_backup(target_path: str, includes: list[str] | None = None) -> dict:
    includes = includes or targets().get("includes", [])
    dest = Path(target_path).expanduser()
    dest.parent.mkdir(parents=True, exist_ok=True)
    manifest = {"created_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
                "files": [], "type": "aether-backup-1"}
    buf = io.BytesIO()
    total = 0
    with tarfile.open(fileobj=buf, mode="w:gz") as tar:
        for root in includes:
            base = Path(root).expanduser()
            if not base.exists():
                continue
            for f in sorted(base.rglob("*")):
                if f.is_file() and ".aether-tmp" not in f.name:
                    try:
                        data = f.read_bytes()
                    except OSError:
                        continue
                    arcname = str(f.relative_to(base.parent))
                    info = tarfile.TarInfo(name=arcname)
                    info.size = len(data)
                    info.mtime = int(f.stat().st_mtime)
                    tar.addfile(info, io.BytesIO(data))
                    manifest["files"].append({
                        "path": arcname, "size": len(data),
                        "sha256": hashlib.sha256(data).hexdigest(),
                        "mtime": info.mtime})
                    total += len(data)
    blob = buf.getvalue()
    final = dest / f"aether-backup-{time.strftime('%Y%m%d-%H%M%S')}.tar.gz"
    final.write_bytes(blob)
    manifest_bytes = json.dumps(manifest).encode()
    (dest / (final.name + ".manifest.json")).write_bytes(manifest_bytes)
    state = {"last_run": manifest["created_at"], "last_backup": str(final),
             "files": len(manifest["files"]), "bytes": total, "verified": False}
    _save_state(state)
    return {"ok": True, "file": str(final), "files": len(manifest["files"]), "bytes": total}


def verify(backup_path: str) -> dict:
    path = Path(backup_path)
    mpath = path.parent / (path.name + ".manifest.json")
    if not path.exists() or not mpath.exists():
        return {"verified": False, "reason": "backup or manifest missing"}
    manifest = json.loads(mpath.read_text())
    try:
        with tarfile.open(path, "r:gz") as tar:
            names = set(tar.getnames())
    except (tarfile.TarError, OSError) as e:
        return {"verified": False, "reason": str(e)}
    missing = [f["path"] for f in manifest["files"] if f["path"] not in names]
    state = _load_state()
    if str(path) == state.get("last_backup"):
        state["verified"] = not missing
        _save_state(state)
    return {"verified": not missing, "missing": missing[:20], "files": len(manifest["files"])}


def _load_state() -> dict:
    return json.loads(STATE.read_text()) if STATE.exists() else {}


def _save_state(state: dict) -> None:
    STATE.parent.mkdir(parents=True, exist_ok=True)
    STATE.write_text(json.dumps(state, indent=2))


def status() -> dict:
    st = _load_state()
    st["targets"] = targets()
    return st
