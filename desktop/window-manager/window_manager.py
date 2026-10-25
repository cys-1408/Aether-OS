"""Window tracking + operations over the real sway tree."""
from __future__ import annotations

import threading

from aether_core.swayipc import SwayIPC

from compositor_adapter import CompositorAdapter


class WindowManager:
    def __init__(self):
        self.adapter = CompositorAdapter()
        self._windows: dict[int, dict] = {}
        self._listeners = []
        self._start_listen()

    # ---------------------------------------------------------------- state
    def _start_listen(self):
        def listen():
            try:
                SwayIPC().subscribe(["window", "workspace"], lambda ev: self._refresh())
            except (ConnectionError, OSError):
                pass  # session-less context; operations will report unreachable
        threading.Thread(target=listen, daemon=True).start()

    def _refresh(self):
        tree = self.adapter.tree()
        windows = {}

        def walk(node):
            if node.get("type") == "con" and node.get("app_id") is not None:
                windows[node["id"]] = {
                    "id": node["id"], "app_id": node.get("app_id"),
                    "title": node.get("name"), "focused": bool(node.get("focused")),
                    "workspace": None, "floating": node.get("type") == "floating_con",
                    "geometry": node.get("rect"),
                }
            for child in node.get("nodes", []) + node.get("floating_nodes", []):
                walk(child)

        if tree:
            walk(tree)
            for ws in tree.get("nodes", []):
                for o in ws.get("nodes", []):
                    for n in self._collect(o):
                        if n in windows:
                            windows[n]["workspace"] = ws.get("name")
        self._windows = windows
        for cb in self._listeners:
            try:
                cb()
            except Exception:
                pass

    @staticmethod
    def _collect(node) -> list[int]:
        out = [node["id"]] if node.get("app_id") is not None else []
        for child in node.get("nodes", []) + node.get("floating_nodes", []):
            out.extend(WindowManager._collect(child))
        return out

    def windows(self) -> list[dict]:
        self._refresh()
        return list(self._windows.values())

    def on_change(self, cb):
        self._listeners.append(cb)

    # ---------------------------------------------------------------- ops
    def _run(self, cmd: str) -> dict:
        return self.adapter.run(cmd)

    def focus_window(self, wid: int) -> dict:
        return self._run(f"[con_id={wid}] focus")

    def close_window(self, wid: int) -> dict:
        return self._run(f"[con_id={wid}] kill")

    def minimize_window(self, wid: int) -> dict:
        return self._run(f"[con_id={wid}] move scratchpad")

    def restore_window(self, wid: int) -> dict:
        return self._run("[con_id={}] scratchpad show; [con_id={}] floating toggle".format(wid, wid))

    def maximize_window(self, wid: int) -> dict:
        return self._run(f"[con_id={wid}] fullscreen toggle")

    def move_window(self, wid: int, x: int, y: int) -> dict:
        return self._run(f"[con_id={wid}] move position {x} {y}")

    def resize_window(self, wid: int, w: int, h: int) -> dict:
        return self._run(f"[con_id={wid}] resize set {w} {h}")

    def switch_workspace(self, name: str) -> dict:
        return self._run(f"workspace {name}")

    def create_workspace(self, name: str) -> dict:
        return self._run(f"workspace {name}")

    def set_opacity(self, wid: int, opacity: float) -> dict:
        return self._run(f"[con_id={wid}] opacity {opacity}")

    def launch_app(self, command: list[str]) -> dict:
        import subprocess
        try:
            subprocess.Popen(command)
            return {"launched": command[0]}
        except OSError as e:
            return {"error": str(e)}
