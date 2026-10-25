import sys
from pathlib import Path
_p = Path(__file__).resolve()
sys.path.insert(0, str(_p.parents[2]))
sys.path.insert(0, str(_p.parents[3] / 'libraries/libaether-core/python'))
"""One toast surface (click to dismiss)."""
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk


class ToastView(Gtk.Window):
    def __init__(self, title: str, body: str):
        super().__init__(type=Gtk.WindowType.TOPLEVEL)
        self.set_decorated(False)
        self.set_default_size(280, -1)
        self.get_style_context().add_class("toast")
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        t = Gtk.Label(label=title, xalign=0)
        t.get_style_context().add_class("fname")
        box.pack_start(t, False, False, 0)
        if body:
            b = Gtk.Label(label=body, xalign=0)
            b.set_line_wrap(True)
            box.pack_start(b, False, False, 0)
        self.add(box)
        self.add_events(Gdk.EventMask.BUTTON_PRESS_MASK)
        self.connect("button-press-event", lambda *_: self.destroy())
