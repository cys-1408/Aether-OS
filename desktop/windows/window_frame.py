import sys
from pathlib import Path
_p = Path(__file__).resolve()
sys.path.insert(0, str(_p.parents[2]))
sys.path.insert(0, str(_p.parents[3] / 'libraries/libaether-core/python'))
"""Shared chrome helpers for shell-owned windows (reference look)."""
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk


def styled_window(title: str, width: int = 420, height: int = 320) -> Gtk.Window:
    win = Gtk.Window(title=title, type=Gtk.WindowType.TOPLEVEL)
    win.set_default_size(width, height)
    win.set_decorated(False)
    win.get_style_context().add_class("aether-window")
    return win
