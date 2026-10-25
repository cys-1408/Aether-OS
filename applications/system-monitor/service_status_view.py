import sys
from pathlib import Path
_p = Path(__file__).resolve()
sys.path.insert(0, str(_p.parents[2]))
sys.path.insert(0, str(_p.parents[3] / 'libraries/libaether-core/python'))
"""Service status: real Health.services with degraded fallback to systemctl."""
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk


class ServiceStatusView(Gtk.Box):
    def __init__(self, app):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        self.app = app
        self.label = Gtk.Label(label="services: …", xalign=0)
        self.label.get_style_context().add_class("sub")
        self.pack_start(self.label, False, False, 0)

    def refresh(self) -> None:
        import threading

        def work():
            data = self.app.services.call("health", "Health.services", {})
            if data:
                states = ", ".join(f"{k}:{v.get('state', '?')}" for k, v in list(data.items())[:6])
            else:
                states = "health service unreachable (system services still run)"
            __import__("gi.repository", fromlist=["GLib"]).GLib.idle_add(self.label.set_text, states)
        threading.Thread(target=work, daemon=True).start()
