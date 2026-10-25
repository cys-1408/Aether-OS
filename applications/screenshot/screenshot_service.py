"""Real captures via grim + slurp (sway) — honest failure reasons."""
from __future__ import annotations

import json
import shutil
import subprocess
import time
from pathlib import Path

SHOTS = Path.home() / "Pictures" / "Screenshots"


def capture(mode: str = "full") -> dict:
    if not shutil.which("grim"):
        return {"ok": False, "reason": "grim not installed (Wayland screenshot tool)"}
    SHOTS.mkdir(parents=True, exist_ok=True)
    path = SHOTS / f"aether-shot-{time.strftime('%Y%m%d-%H%M%S')}.png"
    argv = ["grim", str(path)]
    if mode == "region":
        if not shutil.which("slurp"):
            return {"ok": False, "reason": "slurp not installed (region selection)"}
        try:
            geom = subprocess.run(["slurp"], capture_output=True, text=True, timeout=60).stdout.strip()
            if not geom:
                return {"ok": False, "reason": "region selection cancelled"}
            argv = ["grim", "-g", geom, str(path)]
        except subprocess.TimeoutExpired:
            return {"ok": False, "reason": "region selection timed out"}
    elif mode == "window":
        geom = _focused_window_geometry()
        if not geom:
            return {"ok": False, "reason": "could not determine focused window geometry (need sway session)"}
        argv = ["grim", "-g", geom, str(path)]
    try:
        out = subprocess.run(argv, capture_output=True, text=True, timeout=30)
        ok = out.returncode == 0 and path.exists()
        return {"ok": ok, "file": str(path)} if ok else {"ok": False, "reason": out.stderr.strip()}
    except subprocess.TimeoutExpired:
        return {"ok": False, "reason": "grim timed out"}


def _focused_window_geometry() -> str | None:
    try:
        tree = json.loads(subprocess.run(["swaymsg", "-t", "get_tree", "-r"],
                                         capture_output=True, text=True, timeout=10).stdout)
        def find_focused(node) -> dict | None:
            if node.get("focused"):
                return node
            for child in node.get("nodes", []) + node.get("floating_nodes", []):
                found = find_focused(child)
                if found:
                    return found
            return None
        win = find_focused(tree)
        if win and win.get("rect"):
            r = win["rect"]
            return f"{r['x']},{r['y']} {r['width']}x{r['height']}"
    except (json.JSONDecodeError, subprocess.TimeoutExpired, FileNotFoundError):
        pass
    return None
