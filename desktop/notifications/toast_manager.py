import sys
from pathlib import Path
_p = Path(__file__).resolve()
sys.path.insert(0, str(_p.parents[2]))
sys.path.insert(0, str(_p.parents[3] / 'libraries/libaether-core/python'))
"""Toasts: top-right dark pills, 2.6s, queue max 3, click dismisses."""
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GLib

try:
    gi.require_version("GtkLayerShell", "0.1")
    from gi.repository import GtkLayerShell
    HAS_LAYER = True
except (ImportError, ValueError):
    HAS_LAYER = False

from toast_view import ToastView


class ToastManager:
    def __init__(self, parent_window):
        self.parent_window = parent_window
        self._active: list[Gtk.Window] = []

    def show(self, title: str, body: str = "") -> dict:
        if len(self._active) >= 3:
            self._active[0].destroy()
            self._active.pop(0)
        toast = ToastView(title, body)
        toast.set_transient_for(self.parent_window)
        if HAS_LAYER:
            GtkLayerShell.init_for_window(toast)
            GtkLayerShell.set_layer(toast, GtkLayerShell.Layer.OVERLAY)
            GtkLayerShell.set_anchor(toast, GtkLayerShell.Edge.TOP, True)
            GtkLayerShell.set_anchor(toast, GtkLayerShell.Edge.RIGHT, True)
            GtkLayerShell.set_margin(toast, GtkLayerShell.Edge.TOP, 58 + 52 * len(self._active))
            GtkLayerShell.set_margin(toast, GtkLayerShell.Edge.RIGHT, 20)
        toast.connect("destroy", self._forget)
        toast.show_all()
        self._active.append(toast)
        GLib.timeout_add(2600, self._expire, toast)
        return {"shown": True}

    def _expire(self, toast):
        if toast in self._active:
            toast.destroy()
        return False

    def _forget(self, toast):
        if toast in self._active:
            self._active.remove(toast)
