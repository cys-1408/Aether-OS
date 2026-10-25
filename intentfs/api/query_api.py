"""Query façade over search. — thin façades over the daemon methods."""
from __future__ import annotations

from aether_core.ipc import call
from aether_core import paths


def _intentfs(method: str, params: dict | None = None, timeout: float = 30.0):
    return call(paths.system_socket("intentfs"), method, params or {}, timeout=timeout)


def search(query: str, filters: dict | None = None):
    return _intentfs("IntentFS.search", {"query": query, "filters": filters or {}})


def status():
    return _intentfs("IntentFS.status")
