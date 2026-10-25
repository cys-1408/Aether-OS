import sys
from pathlib import Path
_p = Path(__file__).resolve()
sys.path.insert(0, str(_p.parents[2]))
sys.path.insert(0, str(_p.parents[3] / 'libraries/libaether-core/python'))
"""40px title bar with traffic-dot controls (reference chrome)."""
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk


class TitleBar(Gtk.Box):
    def __init__(self, title: str, on_close, on_min=None, on_max=None):
        super().__init__(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        self.get_style_context().add_class("titlebar")
        self.set_size_request(-1, 40)
        traffic = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=7)
        for color, cb in (("#ff5f57", on_close), ("#ffbd2e", on_min), ("#28ca41", on_max)):
            dot = Gtk.Button(label="")
            dot.get_style_context().add_class("dot")
            dot.set_size_request(11, 11)
            if cb:
                dot.connect("clicked", lambda _b, f=cb: f())
            traffic.pack_start(dot, False, False, 0)
        self.pack_start(traffic, False, False, 14)
        lbl = Gtk.Label(label=title, xalign=0)
        lbl.get_style_context().add_class("wtitle")
        self.pack_start(lbl, True, True, 0)
