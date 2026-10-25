"""Zip/tar archive adapter with strict path-traversal guards.

Extraction refuses any entry whose name contains ``..`` components or is an
absolute path (zip-slip protection) and refuses hard/symlinks by default.
Create supports zip and tar (gz/bz2/xz) via the Python stdlib only.
"""

from __future__ import annotations

import os
import tarfile
import time
import zipfile
from pathlib import Path


class ArchiveSafetyError(ValueError):
    """Raised when an archive member would escape the destination."""


def is_unsafe_member_name(name: str) -> bool:
    if not name:
        return True
    if name.startswith("/") or name.startswith("\\"):
        return True
    if os.path.isabs(name):
        return True
    if ":" in name.split("/", 1)[0] and os.name == "nt":  # windows drive letters
        return True
    parts = name.replace("\\", "/").split("/")
    return ".." in parts


def list_archive(path: Path) -> list:
    """Return entries: name, size, mtime, kind, compressed size."""
    path = Path(path)
    suffixes = path.suffixes
    entries = []
    if zipfile.is_zipfile(path):
        with zipfile.ZipFile(path) as archive:
            for info in archive.infolist():
                entries.append(
                    {
                        "name": info.filename,
                        "size": info.file_size,
                        "compressed": info.compress_size,
                        "mtime": time.mktime(info.date_time + (0, 0, -1))
                        if info.date_time else 0,
                        "kind": "dir" if info.is_dir() else "file",
                    }
                )
        return entries
    if _is_tar(path):
        mode = _tar_mode(path)
        with tarfile.open(path, mode) as archive:
            for member in archive.getmembers():
                entries.append(
                    {
                        "name": member.name,
                        "size": member.size,
                        "compressed": 0,
                        "mtime": int(member.mtime),
                        "kind": "dir" if member.isdir() else
                                "link" if member.issym() or member.islnk() else "file",
                    }
                )
        return entries
    raise ValueError(
        f"Unsupported archive format: {''.join(suffixes) or path.name}"
    )


def _is_tar(path: Path) -> bool:
    return path.suffix in (".tar",) or path.name.endswith(
        (".tar.gz", ".tar.bz2", ".tar.xz", ".tgz", ".tbz2", ".txz")
    )


def _tar_mode(path: Path) -> str:
    name = path.name
    if name.endswith((".tar.gz", ".tgz")):
        return "r:gz"
    if name.endswith((".tar.bz2", ".tbz2")):
        return "r:bz2"
    if name.endswith((".tar.xz", ".txz")):
        return "r:xz"
    return "r:"


def extract(path: Path, dest: Path, policy: str = "ask",
            conflict_reporter=None) -> dict:
    """Extract safely into ``dest``.

    policy: "ask" (report conflicts), "skip", "overwrite", "rename".
    Returns {"extracted": n, "skipped": n, "renamed": n}.
    """
    path, dest = Path(path), Path(dest)
    dest.mkdir(parents=True, exist_ok=True)
    counters = {"extracted": 0, "skipped": 0, "renamed": 0}

    if zipfile.is_zipfile(path):
        with zipfile.ZipFile(path) as archive:
            for info in archive.infolist():
                _extract_zip_member(archive, info, dest, policy, counters, conflict_reporter)
        return counters
    if _is_tar(path):
        with tarfile.open(path, _tar_mode(path)) as archive:
            for member in archive.getmembers():
                _extract_tar_member(archive, member, dest, policy, counters, conflict_reporter)
        return counters
    raise ValueError(f"Unsupported archive format: {path.name}")


def _resolve_safely(dest: Path, name: str) -> Path:
    if is_unsafe_member_name(name):
        raise ArchiveSafetyError(
            f"refusing unsafe archive path: {name!r} (absolute or '..' traversal)"
        )
    target = (dest / name).resolve()
    if not str(target).startswith(str(dest.resolve()) + os.sep) and target != dest.resolve():
        raise ArchiveSafetyError(f"refusing archive path escaping destination: {name!r}")
    return target


def _conflict_resolution(target: Path, policy, reporter) -> str:
    if not target.exists():
        return "extract"
    if policy == "overwrite":
        return "overwrite"
    if policy == "skip":
        return "skip"
    if policy == "rename":
        return "rename"
    decision = reporter(target) if reporter else "skip"
    return decision if decision in ("skip", "overwrite", "rename") else "skip"


def _unique_dest(target: Path) -> Path:
    stem, suffix = target.stem, target.suffix
    counter = 2
    while target.exists():
        target = target.with_name(f"{stem} ({counter}){suffix}")
        counter += 1
        if counter > 1000:
            break
    return target


def _extract_zip_member(archive, info, dest, policy, counters, reporter):
    if info.is_dir():
        _resolve_safely(dest, info.filename).mkdir(parents=True, exist_ok=True)
        return
    target = _resolve_safely(dest, info.filename)
    action = _conflict_resolution(target, policy, reporter)
    if action == "skip":
        counters["skipped"] += 1
        return
    if action == "rename":
        target = _unique_dest(target)
        counters["renamed"] += 1
    elif action == "overwrite":
        if target.is_dir():
            import shutil

            shutil.rmtree(target)
    target.parent.mkdir(parents=True, exist_ok=True)
    with archive.open(info) as source, open(target, "wb") as out:
        _copy_stream(source, out)
    os.utime(target, (time.mktime(info.date_time + (0, 0, -1)) if info.date_time else time.time(),) * 2)
    counters["extracted"] += 1


def _extract_tar_member(archive, member, dest, policy, counters, reporter):
    if member.issym() or member.islnk():
        # Symlinks inside untrusted archives are refused by policy (real safety).
        counters["skipped"] += 1
        return
    if member.isdir():
        _resolve_safely(dest, member.name).mkdir(parents=True, exist_ok=True)
        return
    target = _resolve_safely(dest, member.name)
    action = _conflict_resolution(target, policy, reporter)
    if action == "skip":
        counters["skipped"] += 1
        return
    if action == "rename":
        target = _unique_dest(target)
        counters["renamed"] += 1
    elif action == "overwrite":
        if target.is_dir():
            import shutil

            shutil.rmtree(target)
    target.parent.mkdir(parents=True, exist_ok=True)
    source = archive.extractfile(member)
    if source is None:
        counters["skipped"] += 1
        return
    with source, open(target, "wb") as out:
        _copy_stream(source, out)
    os.utime(target, (member.mtime, member.mtime))
    counters["extracted"] += 1


def _copy_stream(source, out, chunk: int = 1 << 16) -> int:
    total = 0
    while True:
        data = source.read(chunk)
        if not data:
            break
        out.write(data)
        total += len(data)
    return total


CREATE_FORMATS = ("zip", "tar.gz", "tar.bz2", "tar.xz")


def create(archive_path: Path, sources, fmt: str = "zip",
           progress=None) -> dict:
    """Create an archive from files/directories. Returns count + bytes."""
    archive_path = Path(archive_path)
    sources = [Path(s) for s in sources]
    missing = [str(s) for s in sources if not s.exists()]
    if missing:
        raise FileNotFoundError(f"missing source paths: {missing}")

    def common_root():
        if len(sources) == 1:
            return sources[0].parent
        base = os.path.commonpath([str(s) for s in sources])
        return Path(base) if base else Path("/")

    root = common_root()
    count = 0
    total_bytes = 0
    if fmt == "zip":
        with zipfile.ZipFile(archive_path, "w", zipfile.ZIP_DEFLATED) as archive:
            for source in sources:
                if source.is_dir():
                    for file_path in sorted(source.rglob("*")):
                        if file_path.is_file():
                            arcname = file_path.relative_to(root)
                            archive.write(file_path, str(arcname))
                            count += 1
                            total_bytes += file_path.stat().st_size
                            if progress:
                                progress(count, file_path.name)
                else:
                    archive.write(source, source.relative_to(root))
                    count += 1
                    total_bytes += source.stat().st_size
                    if progress:
                        progress(count, source.name)
    elif fmt in ("tar.gz", "tar.bz2", "tar.xz"):
        mode = {"tar.gz": "w:gz", "tar.bz2": "w:bz2", "tar.xz": "w:xz"}[fmt]
        with tarfile.open(archive_path, mode) as archive:
            for source in sources:
                archive.add(source, arcname=str(source.relative_to(root)), recursive=True)
                if source.is_file():
                    count += 1
                    total_bytes += source.stat().st_size
                else:
                    for file_path in source.rglob("*"):
                        if file_path.is_file():
                            count += 1
                            total_bytes += file_path.stat().st_size
                if progress:
                    progress(count, source.name)
    else:
        raise ValueError(f"unsupported create format: {fmt}")
    return {"count": count, "bytes": total_bytes, "path": str(archive_path)}
