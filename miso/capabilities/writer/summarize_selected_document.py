"""summarize: LOCAL inference only (never network)."""
from __future__ import annotations

from pathlib import Path

from aether_core import filesops


def run(params: dict, peer_uid: int = 0) -> dict:
    p = Path(str(params.get("path", ""))).expanduser()
    if not filesops.is_within(p, Path.home()):
        from aether_core.errors import IpcError
        raise IpcError("E_SCOPE", "document outside home")
    text = p.read_text(errors="replace")[:6000] if p.exists() else ""
    from aether_core.ipc import call
    from aether_core import paths as _p
    from aether_core.errors import IpcError as _E
    try:
        result = call(_p.system_socket("runtime"), "Runtime.infer", {
            "request_id": f"sum-{int(__import__('time').time())}", "task_class": "summarize",
            "prompt": text, "max_tokens": 200, "timeout_s": 60}, timeout=70)
        return {"summary": (result or {}).get("text", ""), "local_only": True}
    except _E as e:
        return {"summary": "", "reason": e.message, "local_only": True}
