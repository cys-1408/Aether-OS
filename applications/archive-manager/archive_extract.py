"""Safe extraction: refuse traversal, report conflicts policy."""
from __future__ import annotations

import tarfile
import zipfile
from pathlib import Path


def _is_safe(name: str) -> bool:
    p = Path(name)
    if p.is_absolute() or ".." in p.parts:
        return False
    return True


def extract(archive_path: str, dest: str) -> dict:
    dest_path = Path(dest)
    extracted = 0
    skipped = []
    if zipfile.is_zipfile(archive_path):
        with zipfile.ZipFile(archive_path) as zf:
            for info in zf.infolist():
                if not _is_safe(info.filename):
                    skipped.append(info.filename)
                    continue
                target = dest_path / info.filename
                target.parent.mkdir(parents=True, exist_ok=True)
                if info.is_dir():
                    target.mkdir(exist_ok=True)
                else:
                    target.write_bytes(zf.read(info))
                    extracted += 1
    else:
        with tarfile.open(archive_path, "r:*") as tf:
            for member in tf.getmembers():
                if not member.isfile() and not member.isdir():
                    skipped.append(member.name)
                    continue
                if not _is_safe(member.name):
                    skipped.append(member.name)
                    continue
                target = dest_path / member.name
                target.parent.mkdir(parents=True, exist_ok=True)
                if member.isdir():
                    target.mkdir(exist_ok=True)
                else:
                    src = tf.extractfile(member)
                    target.write_bytes(src.read())
                    extracted += 1
    return {"extracted": extracted, "skipped_unsafe": skipped}
