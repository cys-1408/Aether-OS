"""Minimize (scratchpad) + maximize (fullscreen) semantics."""
from window_manager import WindowManager  # noqa: F401


def minimize(wm: WindowManager, wid: int) -> dict:
    return wm.minimize_window(wid)


def restore(wm: WindowManager, wid: int) -> dict:
    return wm.restore_window(wid)


def toggle_maximize(wm: WindowManager, wid: int) -> dict:
    return wm.maximize_window(wid)
