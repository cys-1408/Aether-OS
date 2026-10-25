"""Full rebuild: clear + re-scan roots (source files untouched)."""
from __future__ import annotations

from pathlib import Path


def rebuild(store, config: dict, scheduler) -> dict:
    cleared = store.clear_all()
    queued = 0
    for root in config.get("watch_roots", []):
        base = Path(str(root).replace("~", str(Path.home()))).expanduser()
        if base.is_dir():
            for p in base.rglob("*"):
                if p.is_file():
                    scheduler.on_changed(str(p))
                    queued += 1
    return {"cleared": cleared, "queued": queued,
            "note": "original files are never modified"}
