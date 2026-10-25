import sys
from pathlib import Path
_p = Path(__file__).resolve()
sys.path.insert(0, str(_p.parents[2]))
sys.path.insert(0, str(_p.parents[3] / 'libraries/libaether-core/python'))
"""'Miso's activity' panel fed by the REAL Action Ledger (never invented)."""
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GLib

try:
    gi.require_version("GtkLayerShell", "0.1")
    from gi.repository import GtkLayerShell
    HAS_LAYER = True
except (ImportError, ValueError):
    HAS_LAYER = False


class ActivityPanel(Gtk.Window):
    def __init__(self, shell):
        super().__init__(title="Miso's activity", type=Gtk.WindowType.TOPLEVEL)
        self.shell = shell
        self.set_size_request(225, 140)
        self.set_decorated(False)
        self.get_style_context().add_class("aether-activity")
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4, border_width=11)
        head = Gtk.Label(label="Miso's activity", xalign=0)
        head.get_style_context().add_class("activity-title")
        box.pack_start(head, False, False, 0)
        self.log = Gtk.Label(label="Settled into the desktop. Watching over things.", xalign=0)
        self.log.set_line_wrap(True)
        self.log.get_style_context().add_class("sub")
        box.pack_start(self.log, False, False, 0)
        self.add(box)
        if HAS_LAYER:
            GtkLayerShell.init_for_window(self)
            GtkLayerShell.set_layer(self, GtkLayerShell.Layer.BOTTOM)
        self._poll()
        GLib.timeout_add_seconds(6, self._poll)

    def _poll(self):
        import threading

        def probe():
            from aether_core.ipc import call
            from aether_core.errors import IpcError
            from aether_core import paths
            try:
                data = call(paths.system_socket("ledger"), "Ledger.query", {"limit": 1}, timeout=4)
                entries = data.get("entries", [])
                if entries:
                    e = entries[0]
                    text = f"{e.get('timestamp', '')} · {e.get('request', {}).get('capability_id', 'action')} → {e.get('result', '')}"
                else:
                    text = "No agent activity yet — everything calm."
            except IpcError as exc:
                text = f"Activity feed unavailable ({exc.message})"
            GLib.idle_add(self.log.set_text, text)
        threading.Thread(target=probe, daemon=True).start()
        return True
