"""Index rebuild: clear + reindex (source files untouched)."""
from __future__ import annotations


def rebuild_index(app) -> str:
    cleared = app.services.call("intentfs", "IntentFS.clear", {"scope": "all"})
    if not cleared:
        return "IntentFS unreachable"
    reindex = app.services.call("intentfs", "IntentFS.reindex", {})
    return f"index cleared ({cleared.get('cleared', '?')} records) · reindex: {reindex}"
