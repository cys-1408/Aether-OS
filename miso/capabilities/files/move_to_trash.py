"""move_to_trash: XDG trash via aether_core (undoable)."""
from __future__ import annotations

from pathlib import Path

from aether_core import filesops


def run(params: dict, peer_uid: int = 0) -> dict:
    result = filesops.trash(Path(str(params.get("path", ""))).expanduser())
    return {"trashed_to": result["trashed_to"], "info": result["info"], "_undo": {"name": Path(result["trashed_to"]).name}}
