"""Path safety + XDG trash (freedesktop Trash spec) + stable file identity.

All operations work on real paths; trash lives at ~/.local/share/Trash
(files/ + info/*.trashinfo) as per the freedesktop spec.
"""
from __future__ import annotations

import hashlib
import os
import re
import shutil
import time
from datetime import datetime, timezone
from pathlib import Path

from .errors import AetherError

HOME = Path.home()
TRASH_ROOT = Path(os.environ.get("XDG_DATA_HOME", HOME / ".local/share")) / "Trash"


def is_within(path: Path, root: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
        return True
    except ValueError:
        return False


def safe_join(root: Path, relative: str) -> Path:
    """Join and refuse traversal outside root."""
    if "\x00" in relative:
        raise AetherError("E_PATH", "NUL byte in path")
    candidate = (root / relative).resolve()
    if not is_within(candidate, root):
        raise AetherError("E_PATH_TRAVERSAL", f"path escapes {root}: {relative}")
    return candidate


def stable_file_id(path: Path) -> str:
    """Stable identity: sha256(dev:inode:size:mtime_ns). Survives rename/move
    on the same filesystem; changes deliberately when content/device changes."""
    st = os.stat(path)
    basis = f"{st.st_dev}:{st.st_ino}:{st.st_size}:{st.st_mtime_ns}"
    return hashlib.sha256(basis.encode()).hexdigest()[:32]


def content_fingerprint(path: Path) -> str:
    """Streaming sha256 of file bytes."""
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 256), b""):
            h.update(chunk)
    return h.hexdigest()


# ---------------------------------------------------------------- trash ----
def _trash_info_name(original: str) -> str:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")
    base = Path(original).name
    safe = re.sub(r"[^A-Za-z0-9._-]", "_", base)
    return f"{stamp}-{safe}.trashinfo"


def trash(path: Path) -> dict:
    """Move a file/dir into the XDG trash. Returns real destination."""
    src = Path(path)
    if not src.exists():
        raise AetherError("E_NOT_FOUND", f"not found: {src}")
    files_dir = TRASH_ROOT / "files"
    info_dir = TRASH_ROOT / "info"
    files_dir.mkdir(parents=True, exist_ok=True)
    info_dir.mkdir(parents=True, exist_ok=True)
    name = src.name
    dest = files_dir / name
    i = 2
    while dest.exists():
        dest = files_dir / f"{name} ({i})"
        i += 1
    shutil.move(str(src), str(dest))
    info = info_dir / (dest.name + ".trashinfo")
    info.write_text(
        "[Trash Info]\n"
        f"Path={src.resolve()}\n"
        f"DeletionDate={datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S')}\n",
        encoding="utf-8",
    )
    return {"trashed_to": str(dest), "info": str(info), "original": str(src)}


def list_trash() -> list[dict]:
    files_dir = TRASH_ROOT / "files"
    out: list[dict] = []
    if not files_dir.exists():
        return out
    for entry in sorted(files_dir.iterdir()):
        info = TRASH_ROOT / "info" / f"{entry.name}.trashinfo"
        original, deleted = "", ""
        if info.exists():
            for line in info.read_text().splitlines():
                if line.startswith("Path="):
                    original = line[5:]
                if line.startswith("DeletionDate="):
                    deleted = line[13:]
        st = entry.stat()
        out.append({"name": entry.name, "path": str(entry), "original": original,
                    "deleted": deleted, "size": st.st_size,
                    "mtime": st.st_mtime})
    return out


def restore(trash_name: str) -> dict:
    """Restore a trashed item. Conflicts get ' (2)' suffixes — never silent overwrite."""
    files_dir = TRASH_ROOT / "files"
    src = files_dir / Path(trash_name).name
    if not src.exists():
        raise AetherError("E_NOT_FOUND", f"not in trash: {trash_name}")
    info = TRASH_ROOT / "info" / f"{src.name}.trashinfo"
    original = ""
    if info.exists():
        for line in info.read_text().splitlines():
            if line.startswith("Path="):
                original = line[5:]
    target = Path(original) if original else HOME / "restored" / src.name
    target.parent.mkdir(parents=True, exist_ok=True)
    final = target
    i = 2
    while final.exists():
        final = target.with_name(f"{target.name} ({i})")
        i += 1
    shutil.move(str(src), str(final))
    if info.exists():
        info.unlink()
    return {"restored_to": str(final), "renamed_due_to_conflict": final != target}


def empty_trash_items(names: list[str]) -> dict:
    """Permanently remove selected trash items (destructive — caller confirms)."""
    removed = []
    for n in names:
        p = TRASH_ROOT / "files" / Path(n).name
        info = TRASH_ROOT / "info" / f"{Path(n).name}.trashinfo"
        if p.is_dir():
            shutil.rmtree(p)
        elif p.exists():
            p.unlink()
        if info.exists():
            info.unlink()
        removed.append(n)
    return {"removed": removed}


def trash_size() -> int:
    total = 0
    files_dir = TRASH_ROOT / "files"
    if files_dir.exists():
        for p in files_dir.rglob("*"):
            if p.is_file():
                total += p.stat().st_size
    return total
