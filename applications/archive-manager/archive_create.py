"""Create zip/tar.gz archives from chosen files."""
from __future__ import annotations

import tarfile
import zipfile
from pathlib import Path


def create(archive_path: str, members: list[str]) -> dict:
    ap = Path(archive_path)
    count = 0
    if ap.suffix == ".zip":
        with zipfile.ZipFile(ap, "w", zipfile.ZIP_DEFLATED) as zf:
            for m in members:
                p = Path(m)
                if p.is_file():
                    zf.write(p, arcname=p.name)
                    count += 1
    else:
        mode = "w:gz" if str(ap).endswith(".gz") else "w"
        with tarfile.open(ap, mode) as tf:
            for m in members:
                p = Path(m)
                if p.is_file():
                    tf.add(p, arcname=p.name)
                    count += 1
    return {"archive": str(ap), "members": count}
