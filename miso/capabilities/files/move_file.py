"""move_file: real move."""
from __future__ import annotations

import shutil
from pathlib import Path


def run(params: dict, peer_uid: int = 0) -> dict:
    src = Path(str(params.get("src", ""))).expanduser()
    dst = Path(str(params.get("dst", ""))).expanduser()
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(str(src), str(dst))
    return {"dst": str(dst)}
