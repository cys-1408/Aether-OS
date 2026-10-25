"""Capability recommend_model — return the Runtime's current
compatibility-ranked recommendations for a task class (read-only)."""

from __future__ import annotations

from aether_core import paths
from aether_core.errors import IpcError

RUNTIME_SOCK = str(paths.system_socket("runtime"))


def _runtime_call(method: str, params: dict, timeout: float):
    from aether_core.ipc import call
    return call(RUNTIME_SOCK, method, params, timeout=timeout)


def execute(params: dict, ctx: dict | None = None) -> dict:
    if not isinstance(params, dict):
        params = {}
    task_class = str(params.get("task_class", "assistant"))[:64]
    try:
        result = _runtime_call("Runtime.models_recommend",
                               {"task_class": task_class}, 30.0)
    except IpcError as e:
        return {"recommendations": [], "available": False, "reason": str(e)}
    recs = result.get("recommendations", []) if isinstance(result, dict) else []
    return {"recommendations": recs,
            "available": True, "task_class": task_class}


def run(params: dict, peer_uid: int | None = None) -> dict:
    return execute(params, ctx={"uid": peer_uid} if peer_uid is not None else None)
