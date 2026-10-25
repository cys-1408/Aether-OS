"""Clock widget used by quick settings + lock screen (locale aware)."""
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GLib


class ClockWidget(Gtk.Label):
    def __init__(self, with_seconds: bool = True):
        super().__init__(label="")
        self._fmt = "%H:%M:%S" if with_seconds else "%H:%M"
        self._tick()
        GLib.timeout_add_seconds(1, self._tick)

    def _tick(self):
        from gi.repository import GLib as _g
        self.set_text(_g.DateTime.new_now_local().format(self._fmt))
        return True
