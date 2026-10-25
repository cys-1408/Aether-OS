import sys
from pathlib import Path
_p = Path(__file__).resolve()
sys.path.insert(0, str(_p.parents[2]))
sys.path.insert(0, str(_p.parents[3] / 'libraries/libaether-core/python'))
"""Focus timer readout for the Focus app window."""
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk


class FocusTimerView(Gtk.Box):
    def __init__(self, focus):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        self.focus = focus
        self.label = Gtk.Label(label="25:00")
        self.label.get_style_context().add_class("h1")
        self.pack_start(self.label, False, False, 0)
        from gi.repository import GLib
        GLib.timeout_add_seconds(1, self._tick)

    def _tick(self):
        if self.focus.active and self.focus.remaining is not None:
            m, s = divmod(max(0, self.focus.remaining), 60)
            self.label.set_text(f"{m:02d}:{s:02d}")
        else:
            self.label.set_text("—")
        return True
