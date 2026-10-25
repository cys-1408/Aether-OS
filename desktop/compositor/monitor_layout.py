"""Saved multi-monitor profiles (real sway output geometry)."""
from __future__ import annotations

import json
from pathlib import Path

from aether_core import paths
from display_manager import outputs

PROFILE_DIR = paths.USER_CONFIG_DIR / "monitor-profiles"


def save_profile(name: str) -> dict:
    PROFILE_DIR.mkdir(parents=True, exist_ok=True)
    prof = [{"name": o.get("name"), "mode": o.get("mode"),
             "scale": (o.get("scale") or 1.0), "x": o.get("layout", {}).get("x", 0)}
            for o in outputs()]
    (PROFILE_DIR / f"{name}.json").write_text(json.dumps(prof, indent=2))
    return {"saved": name, "outputs": prof}


def apply_profile(name: str) -> dict:
    p = PROFILE_DIR / f"{name}.json"
    if not p.exists():
        return {"ok": False, "error": f"profile {name} not saved"}
    prof = json.loads(p.read_text())
    results = []
    for o in prof:
        from display_manager import set_mode, set_scale, set_position
        results.append(set_mode(o["name"], o["mode"]))
        results.append(set_scale(o["name"], o["scale"]))
        results.append(set_position(o["name"], o["x"], 0))
    return {"ok": all(r.get("ok") for r in results), "results": results}
