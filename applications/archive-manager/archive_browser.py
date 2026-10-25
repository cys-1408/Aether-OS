"""List archive members (zip/tar family) with sizes."""
from __future__ import annotations

import tarfile
import zipfile


def list_archive(path: str) -> list[tuple[str, int]]:
    members = []
    if zipfile.is_zipfile(path):
        with zipfile.ZipFile(path) as zf:
            for info in zf.infolist():
                members.append((info.filename, info.file_size))
    else:
        try:
            with tarfile.open(path, "r:*") as tf:
                for m in tf.getmembers():
                    members.append((m.name, m.size))
        except tarfile.TarError as e:
            raise ValueError(f"unsupported archive: {e}") from e
    return members
