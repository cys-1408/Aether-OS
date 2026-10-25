"""restore_from_trash: conflict-safe restore."""
from __future__ import annotations

from aether_core import filesops


def run(params: dict, peer_uid: int = 0) -> dict:
    result = filesops.restore(str(params.get("name", "")))
    return {"restored_to": result["restored_to"],
            "renamed_due_to_conflict": result.get("renamed_due_to_conflict", False)}
