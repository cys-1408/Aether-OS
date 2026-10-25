"""Periodic full-scan reconciliation (mtime/size based)."""
from __future__ import annotations

from pathlib import Path


def reconcile(store, roots: list[str], config: dict) -> dict:
    changed = 0
    for root in roots:
        base = Path(str(root).replace("~", str(Path.home()))).expanduser()
        if not base.exists():
            continue
        for p in base.rglob("*"):
            if not p.is_file():
                continue
            try:
                st = p.stat()
            except OSError:
                continue
            rec = store.get_by_path(str(p))
            if rec and rec.get("mtime") == st.st_mtime and rec.get("size_bytes") == st.st_size:
                continue
            changed += 1
    return {"reconciled_changes": changed}
