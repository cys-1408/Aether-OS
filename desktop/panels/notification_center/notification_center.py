import sys
from pathlib import Path
_p = Path(__file__).resolve()
sys.path.insert(0, str(_p.parents[2]))
sys.path.insert(0, str(_p.parents[3] / 'libraries/libaether-core/python'))
"""Notification center: real history from the notifications service."""
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

try:
    gi.require_version("GtkLayerShell", "0.1")
    from gi.repository import GtkLayerShell
    HAS_LAYER = True
except (ImportError, ValueError):
    HAS_LAYER = False


class NotificationCenter(Gtk.Window):
    def __init__(self, shell):
        super().__init__(title="Notifications", type=Gtk.WindowType.TOPLEVEL)
        self.shell = shell
        self.set_size_request(320, 380)
        self.set_decorated(False)
        self.get_style_context().add_class("aether-panel")
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6, border_width=12)
        head = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        head.pack_start(Gtk.Label(label="Notifications", xalign=0), True, True, 0)
        close = Gtk.Button(label="×")
        close.connect("clicked", lambda _: self.hide())
        head.pack_end(close, False, False, 0)
        box.pack_start(head, False, False, 0)
        self.list_box = Gtk.ListBox()
        scroll = Gtk.ScrolledWindow()
        scroll.set_vexpand(True)
        scroll.add(self.list_box)
        box.pack_start(scroll, True, True, 0)
        self.add(box)
        self.refresh()
        if HAS_LAYER:
            GtkLayerShell.init_for_window(self)
            GtkLayerShell.set_layer(self, GtkLayerShell.Layer.TOP)

    def refresh(self):
        import threading
        from notification_item import NotificationItem

        def probe():
            from aether_core.ipc import call
            from aether_core.errors import IpcError
            from aether_core import paths
            try:
                data = call(paths.system_socket("notifications"), "Notify.list", {}, timeout=4)
                items = data.get("notifications", [])
            except IpcError as e:
                items = [{"id": "", "title": "Notification service unreachable",
                          "body": e.message, "source": "system"}]
            GLib = __import__("gi.repository", fromlist=["GLib"]).GLib
            GLib.idle_add(self._apply, items)
        threading.Thread(target=probe, daemon=True).start()

    def _apply(self, items):
        for child in self.list_box.get_children():
            self.list_box.remove(child)
        for item in items:
            self.list_box.add(NotificationItem(item, self))
        self.list_box.show_all()
        return False
