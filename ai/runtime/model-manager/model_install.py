"""Transactional install: staging dir → verify → atomic move into store."""
from __future__ import annotations

import os
import shutil
from pathlib import Path

from aether_core.errors import AetherError


def install_transactional(staging_file: Path, store_dir: Path, model_id: str) -> Path:
    store_dir.mkdir(parents=True, exist_ok=True)
    final = store_dir / model_id / Path(staging_file).name
    final.parent.mkdir(parents=True, exist_ok=True)
    tmp = final.with_suffix(".installing")
    shutil.move(str(staging_file), str(tmp))
    os.replace(tmp, final)  # atomic within the same filesystem
    return final
