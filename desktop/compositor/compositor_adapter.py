"""sway IPC adapter with truthful error surfacing."""
from __future__ import annotations

from aether_core.swayipc import SwayIPC


class CompositorAdapter:
    def __init__(self):
        self._ipc = None

    def ipc(self) -> SwayIPC:
        if self._ipc is None:
            self._ipc = SwayIPC()
        return self._ipc

    def run(self, cmd: str) -> dict:
        try:
            results = self.ipc().run_command(cmd)
            ok = all(r.get("success", False) for r in results)
            err = "; ".join(r.get("error", "") for r in results if not r.get("success"))
            return {"ok": ok, "error": err or None, "results": results}
        except (ConnectionError, OSError) as e:
            return {"ok": False, "error": f"sway IPC unreachable: {e}"}

    def tree(self) -> dict | None:
        try:
            return self.ipc().get_tree()
        except (ConnectionError, OSError):
            return None
