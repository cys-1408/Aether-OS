"""Tiling/arrangement: compute a real grid, emit floating geometry."""
from __future__ import annotations

import math

from window_manager import WindowManager


def tile_windows(wm: WindowManager, window_ids: list[int] | None = None) -> dict:
    wins = window_ids or [w["id"] for w in wm.windows()]
    if not wins:
        return {"ok": False, "error": "no windows to tile"}
    # usable area = output geometry minus bars
    tree = wm.adapter.tree()
    area = {"x": 0, "y": 43, "w": 1920, "h": 1080 - 43 - 60}
    for out in (tree or {}).get("nodes", []):
        if out.get("type") == "output" and out.get("rect", {}).get("width"):
            area = {"x": out["rect"]["x"], "y": out["rect"]["y"] + 43,
                    "w": out["rect"]["width"], "h": out["rect"]["height"] - 43 - 60}
            break
    n = len(wins)
    cols = math.ceil(math.sqrt(n))
    rows = math.ceil(n / cols)
    cw, ch = area["w"] // cols, area["h"] // rows
    results = []
    for i, wid in enumerate(wins):
        col, row = i % cols, i // cols
        x = area["x"] + col * cw + 8
        y = area["y"] + row * ch + 8
        results.append(wm.move_window(wid, x, y))
        results.append(wm.resize_window(wid, cw - 16, ch - 16))
    return {"ok": all(r.get("ok", True) for r in results), "tiled": len(wins)}


def arrange_side_by_side(wm: WindowManager) -> dict:
    wins = [w["id"] for w in wm.windows()]
    return tile_windows(wm, wins[:2])
