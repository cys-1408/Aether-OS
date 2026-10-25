"""aether-agent (Miso) — user-scope daemon."""
from __future__ import annotations

import os
import sys
from pathlib import Path

_p = Path(__file__).resolve()
sys.path.insert(0, str(_p.parents[3] / "libraries/libaether-core/python"))
sys.path.insert(0, str(_p.parent))
sys.path.insert(0, str(_p.parents[1] / "runtime-client"))

from aether_core.ipc import JsonRpcServer  # noqa: E402
from aether_core.config import load_yaml  # noqa: E402
from aether_core.logging_setup import configure_logging  # noqa: E402
from aether_core import paths  # noqa: E402
from aether_core.version import API_VERSIONS  # noqa: E402

from agent_service import AgentService  # noqa: E402
from conversation_state import ConversationState  # noqa: E402

log = configure_logging("agent")


def main() -> int:
    config = load_yaml("/etc/aether/miso.yaml") or {}
    svc = AgentService(config)
    convo = ConversationState()

    def submit(params: dict) -> dict:
        text = str(params.get("text", "")).strip()
        if not text:
            from aether_core.errors import IpcError
            raise IpcError("E_INVALID", "text required")
        convo.append("user", text)
        result = svc.submit(text, uid=params.get("uid", os.getuid()))
        return result

    def poll_result(params: dict) -> dict:
        task = svc.status(params.get("task_id"))
        if isinstance(task, dict) and task.get("state") in ("done", "failed", "cancelled"):
            reply = task.get("reply", "")
            if reply:
                convo.append("miso", reply)
        return task

    methods = {
        "Agent.submit": submit,
        "Agent.status": lambda p: svc.status(p.get("task_id")),
        "Agent.result": poll_result,
        "Agent.cancel": lambda p: svc.cancel(str(p.get("task_id", ""))),
        "Agent.history": lambda p: convo.history(),
        "X.info": lambda p: {"service": "agent", "api_version": API_VERSIONS["agent"]},
    }
    paths.ensure_user_dirs()
    server = JsonRpcServer(paths.user_socket("agent"), methods)
    log.info("miso agent listening")
    server.serve_forever()
    return 0


if __name__ == "__main__":
    sys.exit(main())
