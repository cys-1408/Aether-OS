"""Per-type size limits from config."""
from __future__ import annotations


def within_limits(path, config: dict) -> dict:
    max_mb = int(config.get("max_file_size_mb", 20))
    try:
        size = path.stat().st_size
    except OSError as e:
        return {"ok": False, "reason": str(e)}
    if size > max_mb * 1024 * 1024:
        return {"ok": False, "reason": f"file exceeds {max_mb}MB limit"}
    return {"ok": True, "size": size}
