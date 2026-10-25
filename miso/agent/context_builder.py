"""Approved-context assembly (current app + recent files via IntentFS)."""
from __future__ import annotations


def build_context(services, max_items: int = 5) -> dict:
    context = {"cwd": None, "recent_files": []}
    try:
        from aether_core.ipc import call
        from aether_core import paths
        result = call(paths.system_socket("intentfs"), "IntentFS.search",
                      {"query": "", "filters": {"limit": max_items}}, timeout=5)
        if result:
            context["recent_files"] = [r.get("path") for r in result.get("results", [])[:max_items]]
    except Exception:
        pass
    return context
