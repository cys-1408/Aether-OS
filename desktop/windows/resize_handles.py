"""Resize handles for floating windows (compositor-backed)."""
from __future__ import annotations


def attach(win, wm, wid: int):
    """Register edge drag -> resize via compositor for real windows."""
    def on_edge(gesture_x, gesture_y, edge):
        wm.adapter.run(f"[con_id={wid}] resize {edge} {gesture_x} {gesture_y}")
    return on_edge
