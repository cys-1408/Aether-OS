"""Dimming helpers (per-window sway opacity; honors distraction-protection)."""
from __future__ import annotations


def dim_all_except(wm, target_app: str | None):
    for win in wm.windows():
        if target_app and target_app in (win.get("app_id") or ""):
            wm.set_opacity(win["id"], 1.0)
        else:
            wm.set_opacity(win["id"], 0.15)


def restore(wm):
    for win in wm.windows():
        wm.set_opacity(win["id"], 1.0)
