"""Miso agent service core."""
from __future__ import annotations

import threading
import time

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "capability-os/registry"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "safety"))
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "libraries/libaether-core/python"))

from capability_registry import load_registry  # noqa: E402
from untrusted_content_boundary import wrap_untrusted  # noqa: E402
from aether_core import paths  # noqa: E402


class AgentService:
    def __init__(self, config: dict):
        self.config = config
        self.registry = load_registry()
        self.tasks: dict[str, dict] = {}

    def submit(self, text: str, uid: int) -> dict:
        task_id = f"t-{int(time.time()*1000)}"
        task = {"task_id": task_id, "text": text, "uid": uid,
                "state": "planning", "started_at": time.time()}
        self.tasks[task_id] = task
        threading.Thread(target=self._run, args=(task,), daemon=True).start()
        return {"task_id": task_id, "accepted": True}

    def _run(self, task: dict) -> None:
        from task_planner import build_plan
        from execution_orchestrator import execute_plan
        from response_composer import compose
        try:
            plan = build_plan(task["text"], self.registry, self.config)
            task["plan"] = plan
            task["state"] = "awaiting_confirmation" if plan.get("needs_confirmation") else "executing"
            if plan.get("needs_confirmation"):
                task["confirmation"] = self._request_confirmation(plan)
                if not task["confirmation"]:
                    task["state"] = "cancelled"
                    return
            results = execute_plan(plan, self.registry, self.config, uid=task["uid"])
            task["results"] = results
            task["state"] = "done"
            task["reply"] = compose(task, results)
        except Exception as e:  # noqa: BLE001 — truthful errors to the user
            task["state"] = "failed"
            task["reply"] = f"I hit a snag: {e}. Nothing was changed."
        task["finished_at"] = time.time()

    def _request_confirmation(self, plan: dict) -> bool:
        """Ask the shell to render the real permission dialog (broker flow)."""
        from aether_core.ipc import call
        from aether_core.errors import IpcError
        try:
            result = call(paths.user_socket("shell"), "Broker.confirm", {
                "capability_id": plan["steps"][0]["capability_id"] if plan.get("steps") else "action",
                "risk_class": plan.get("steps", [{}])[0].get("risk_class", "write"),
                "targets": [s.get("params") for s in plan.get("steps", [])],
                "summary": plan.get("intent"),
            }, timeout=300)
            return bool(result and result.get("approved"))
        except IpcError:
            return False

    def status(self, task_id: str | None = None) -> dict:
        if task_id:
            return self.tasks.get(task_id, {"state": "unknown"})
        return {"tasks": [{"id": k, "state": v["state"]} for k, v in list(self.tasks.items())[-10:]]}

    def cancel(self, task_id: str) -> dict:
        task = self.tasks.get(task_id)
        if task:
            task["state"] = "cancelled"
            return {"cancelled": task_id}
        return {"cancelled": False, "reason": "unknown task"}
