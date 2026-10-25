"""Focus state readout used by the Focus app and chip."""
from __future__ import annotations


def render(focus) -> str:
    if not focus.active:
        return "no session"
    state = "paused" if focus.paused else "running"
    m, s = divmod(max(0, focus.remaining or 0), 60)
    return f"{state} · {m:02d}:{s:02d} remaining"
