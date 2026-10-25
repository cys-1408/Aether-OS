"""show_file_metadata: real stat + IntentFS record when present."""
from __future__ import annotations

import datetime
from pathlib import Path


def run(params: dict, peer_uid: int = 0) -> dict:
    p = Path(str(params.get("path", ""))).expanduser()
    if not p.exists():
        from aether_core.errors import IpcError
        raise IpcError("E_NOT_FOUND", f"not found: {p}")
    st = p.stat()
    record = {"path": str(p), "size_bytes": st.st_size,
              "modified": datetime.datetime.fromtimestamp(st.st_mtime).isoformat(),
              "mode": oct(st.st_mode & 0o777)}
    try:
        from aether_core.ipc import call
        from aether_core import paths
        rec = call(paths.system_socket("intentfs"), "IntentFS.metadata", {"path": str(p)}, timeout=5)
        if rec:
            record["index_record"] = rec
    except Exception:
        record["index_record"] = None
    return {"record": record}
