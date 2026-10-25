import sys
from pathlib import Path
_p = Path(__file__).resolve()
sys.path.insert(0, str(_p.parents[2]))
sys.path.insert(0, str(_p.parents[3] / 'libraries/libaether-core/python'))
"""Speech bubble anchored near the companion."""
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GLib


class SpeechBubble(Gtk.Window):
    def __init__(self):
        super().__init__(type=Gtk.WindowType.TOPLEVEL)
        self.set_decorated(False)
        self.get_style_context().add_class("aether-panel")
        self.label = Gtk.Label(label="", xalign=0)
        self.label.set_max_width_chars(40)
        self.label.set_line_wrap(True)
        self.add(self.label)
        self.set_keep_above(True)
        self.hide()

    def show_text(self, text: str, seconds: float = 3.0):
        self.label.set_text(text)
        self.show_all()
        GLib.timeout_add(int(seconds * 1000), self.hide)

    def hide(self, *_):
        super().hide()
