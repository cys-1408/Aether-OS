import sys
from pathlib import Path
_p = Path(__file__).resolve()
sys.path.insert(0, str(_p.parents[2]))
sys.path.insert(0, str(_p.parents[3] / 'libraries/libaether-core/python'))
"""Top bar: brand mark, live status, clock — layer-shell TOP, 43px."""
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GLib

try:
    gi.require_version("GtkLayerShell", "0.1")
    from gi.repository import GtkLayerShell
    HAS_LAYER = True
except (ImportError, ValueError):
    HAS_LAYER = False


class TopBar(Gtk.Box):
    def __init__(self, shell):
        super().__init__(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        self.shell = shell
        self.get_style_context().add_class("aether-topbar")
        self.set_hexpand(True)

        brand = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        mark = Gtk.Label(label="a")
        mark.get_style_context().add_class("brand-mark")
        name = Gtk.Label(label="Aether")
        name.get_style_context().add_class("brand-name")
        sub = Gtk.Label(label="/ Miso desktop companion")
        sub.get_style_context().add_class("brand-sub")
        brand.pack_start(mark, False, False, 0)
        brand.pack_start(name, False, False, 0)
        brand.pack_start(sub, False, False, 0)
        self.pack_start(brand, False, False, 12)

        self.status = Gtk.Label(label="\u25cf All calm")
        self.status.get_style_context().add_class("top-status")
        self.pack_end(Gtk.Label(), True, True, 0)
        self.pack_end(self.status, False, False, 12)
        self.clock = Gtk.Label(label="")
        self.clock.get_style_context().add_class("top-clock")
        self.pack_end(self.clock, False, False, 6)

        self._tick()
        GLib.timeout_add_seconds(1, self._tick)
        self._poll_services()
        GLib.timeout_add_seconds(5, self._poll_services)
        self._apply_layer()

    def _apply_layer(self):
        if HAS_LAYER:
            GtkLayerShell.init_for_window(self)
            GtkLayerShell.set_layer(self, GtkLayerShell.Layer.TOP)
            GtkLayerShell.set_anchor(self, GtkLayerShell.Edge.TOP, True)
            GtkLayerShell.set_anchor(self, GtkLayerShell.Edge.LEFT, True)
            GtkLayerShell.set_anchor(self, GtkLayerShell.Edge.RIGHT, True)
            GtkLayerShell.set_exclusive_zone(self, 43)

    def _tick(self):
        from gi.repository import GLib as _g
        now = _g.DateTime.new_now_local().format("%H:%M:%S")
        self.clock.set_text(now)
        return True

    def _poll_services(self):
        import threading

        def probe():
            from shell_startup import startup_checks
            checks = startup_checks()
            degraded = [k for k, v in checks.items() if v.startswith("unreachable")]
            GLib.idle_add(self._apply_checks, checks, degraded)
        threading.Thread(target=probe, daemon=True).start()
        return True

    def _apply_checks(self, checks, degraded):
        if degraded:
            self.status.set_text(f"\u25cf {', '.join(degraded)} unavailable")
            self.status.get_style_context().add_class("top-status-degraded")
        else:
            self.status.set_text("\u25cf All calm")
            self.status.get_style_context().remove_class("top-status-degraded")
        return False

    def set_status(self, text: str):
        self.status.set_text(f"\u25cf {text}")
