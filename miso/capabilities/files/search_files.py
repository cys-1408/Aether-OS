"""search_files: IntentFS first, filename fallback (honest labeling)."""
from __future__ import annotations

from pathlib import Path


def run(params: dict, peer_uid: int = 0) -> dict:
    query = str(params.get("query", "")).strip()
    from aether_core.ipc import call
    from aether_core.errors import IpcError
    from aether_core import paths
    try:
        data = call(paths.system_socket("intentfs"), "IntentFS.search",
                    {"query": query, "filters": {"limit": 20}}, timeout=25)
        if data:
            return {"results": data.get("results", []), "channel": "intentfs"}
    except IpcError:
        pass
    home = Path.home()
    hits = []
    for p in sorted(home.rglob(f"*{query}*")):
        if p.is_file() and len(hits) < 20:
            hits.append({"filename": p.name, "path": str(p), "reasons": ["filename match"]})
    return {"results": hits, "channel": "filename-fallback"}
