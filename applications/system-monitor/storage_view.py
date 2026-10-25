"""Storage view data (real disk usage)."""
from __future__ import annotations

import shutil
from pathlib import Path


def mounts() -> list[dict]:
    out = []
    for m in ("/", "/home", "/tmp"):
        try:
            u = shutil.disk_usage(m)
            out.append({"mount": m, "total_gb": round(u.total / 1e9, 1),
                        "free_gb": round(u.free / 1e9, 1), "used_pct": round(u.used / u.total * 100, 1)})
        except OSError:
            continue
    return out
