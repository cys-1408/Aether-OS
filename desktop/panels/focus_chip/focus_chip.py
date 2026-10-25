import sys
from pathlib import Path
_p = Path(__file__).resolve()
sys.path.insert(0, str(_p.parents[2]))
sys.path.insert(0, str(_p.parents[3] / 'libraries/libaether-core/python'))
"""Dark focus pill with live countdown + Pause/End (real controller state)."""
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GLib

try:
    gi.require_version("GtkLayerShell", "0.1")
    from gi.repository import GtkLayerShell
    HAS_LAYER = True
except (ImportError, ValueError):
    HAS_LAYER = False


class FocusChip(Gtk.Window):
    def __init__(self, shell):
        super().__init__(type=Gtk.WindowType.TOPLEVEL)
        self.shell = shell
        self.set_decorated(False)
        self.get_style_context().add_class("focus-chip")
        row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        row.pack_start(Gtk.Label(label="● FOCUS SESSION"), False, False, 0)
        self.clock = Gtk.Label(label="25:00")
        self.clock.get_style_context().add_class("focus-clock")
        row.pack_start(self.clock, False, False, 0)
        self.pause_btn = Gtk.Button(label="Pause")
        self.pause_btn.get_style_context().add_class("chip-btn")
        self.pause_btn.connect("clicked", lambda _: self.shell.focus.pause())
        end_btn = Gtk.Button(label="End")
        end_btn.get_style_context().add_class("chip-btn")
        end_btn.connect("clicked", lambda _: self.shell.focus.end())
        row.pack_start(self.pause_btn, False, False, 0)
        row.pack_start(end_btn, False, False, 0)
        self.add(row)
        self.hide()
        GLib.timeout_add_seconds(1, self._tick)
        if HAS_LAYER:
            GtkLayerShell.init_for_window(self)
            GtkLayerShell.set_layer(self, GtkLayerShell.Layer.OVERLAY)

    def update(self, active: bool, remaining: int | None):
        if active:
            self.show_all()
            self.pause_btn.set_text("Pause")
        else:
            self.hide()

    def _tick(self):
        fc = self.shell.focus
        if fc.active and not fc.paused and fc.remaining is not None:
            m, s = divmod(max(0, fc.remaining), 60)
            self.clock.set_text(f"{m:02d}:{s:02d}")
        return True
