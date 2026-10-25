"""Floating move/resize via real compositor geometry commands."""
from window_manager import WindowManager  # noqa: F401


def move_to(wm: WindowManager, wid: int, x: int, y: int) -> dict:
    return wm.move_window(wid, x, y)


def resize_to(wm: WindowManager, wid: int, w: int, h: int) -> dict:
    return wm.resize_window(wid, w, h)
