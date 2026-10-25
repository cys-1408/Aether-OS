"""index_file: queue a reindex via IntentFS."""
from __future__ import annotations

from pathlib import Path

from aether_core.ipc import call
from aether_core import paths


def run(params: dict, peer_uid: int = 0) -> dict:
    result = call(paths.system_socket("intentfs"), "IntentFS.reindex",
                  {"path": str(params.get("path", ""))}, timeout=30)
    return {"queued": result.get("queued", 0)}
