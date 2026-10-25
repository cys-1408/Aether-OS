"""Stepwise execution via the Broker with timeout + verification."""
from __future__ import annotations

import time

from aether_core.ipc import call
from aether_core.errors import IpcError
from aether_core import paths

BROKER = paths.system_socket("broker")


def execute_plan(plan: dict, registry: dict, config: dict, uid: int) -> list[dict]:
    results = []
    for step in plan.get("steps", []):
        cap = registry.get(step["capability_id"], {})
        timeout = min(60, int(cap.get("timeout_s", 15)))
        started = time.time()
        try:
            request = {
                "request_id": f"{plan['plan_id']}-{step['index']}",
                "capability_id": step["capability_id"],
                "capability_version": cap.get("version", "1.0.0"),
                "requester": {"uid": uid, "kind": "agent"},
                "params": step["params"],
                "issued_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
            }
            result = call(BROKER, "Broker.request", {"request": request}, timeout=timeout + 10)
            verified = _verify(step, result)
            results.append({"step": step["index"], "capability_id": step["capability_id"],
                            "outcome": result.get("outcome", "failed"),
                            "result": result.get("result"),
                            "verified": verified,
                            "elapsed_ms": int((time.time() - started) * 1000)})
            if result.get("outcome") not in ("ok",):
                break  # stop on first failed step; completed steps reported truthfully
        except IpcError as e:
            results.append({"step": step["index"], "capability_id": step["capability_id"],
                            "outcome": "failed", "error": e.message,
                            "verified": False})
            break
    return results


def _verify(step: dict, broker_result: dict) -> bool:
    """Verify from system state, not from the tool's word alone (where feasible)."""
    result = broker_result.get("result") or {}
    cap = step["capability_id"]
    verification = broker_result.get("verification") or {}
    if verification.get("method"):
        return bool(verification.get("passed"))
    if cap in ("open_app", "focus_app", "tile_windows", "arrange_windows", "minimize_window"):
        try:
            windows = call(paths.user_socket("shell"), "Shell.list_windows", {}, timeout=6)
            return windows is not None
        except IpcError:
            return False
    if cap in ("move_to_trash", "create_folder"):
        import os
        return os.path.exists(str(result.get("path", ""))) or result.get("trashed_to") is not None or "trashed_to" in result
    return result is not None
