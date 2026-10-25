import sys
from pathlib import Path
_p = Path(__file__).resolve()
sys.path.insert(0, str(_p.parents[2]))
sys.path.insert(0, str(_p.parents[3] / 'libraries/libaether-core/python'))
"""Launcher window: search + launch real apps and registered actions."""
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk, GLib


class AppLauncher(Gtk.Window):
    def __init__(self, shell):
        super().__init__(title="Launcher", type=Gtk.WindowType.TOPLEVEL)
        self.shell = shell
        self.set_default_size(460, 420)
        self.set_decorated(False)
        self.get_style_context().add_class("aether-panel")
        self.set_keep_above(True)
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8, border_width=14)
        self.search = Gtk.Entry()
        self.search.set_placeholder_text("Search apps and actions…")
        self.search.connect("changed", self._filter)
        self.search.connect("activate", self._activate_first)
        box.pack_start(self.search, False, False, 0)
        self.list_box = Gtk.ListBox()
        scroll = Gtk.ScrolledWindow()
        scroll.set_vexpand(True)
        scroll.add(self.list_box)
        box.pack_start(scroll, True, True, 0)
        self.add(box)
        self.hide()
        self._catalog()

    def _catalog(self):
        from app_catalog import build_catalog
        self.items = build_catalog()
        self._fill()

    def _fill(self, query: str = ""):
        for c in self.list_box.get_children():
            self.list_box.remove(c)
        q = query.lower()
        for item in self.items:
            if q and q not in item["name"].lower() and q not in item.get("kind", ""):
                continue
            row = Gtk.ListBoxRow()
            row.item = item
            lbl = Gtk.Label(label=item["name"], xalign=0)
            lbl.set_margin_top(6); lbl.set_margin_bottom(6); lbl.set_margin_start(6)
            row.add(lbl)
            self.list_box.add(row)
        self.list_box.show_all()

    def _filter(self, entry):
        self._fill(entry.get_text())

    def _activate_first(self, *_):
        rows = self.list_box.get_children()
        if rows:
            self._run(rows[0])

    def _run(self, row):
        import subprocess
        item = row.item
        if item["kind"] == "app":
            subprocess.Popen(["sh", "-c", item["exec"]])
        elif item["kind"] == "action":
            self._invoke_action(item)
        self.hide()

    def _invoke_action(self, item):
        """Registered system actions only — never model output."""
        from aether_core.ipc import call
        from aether_core import paths
        try:
            call(paths.resolve_socket(item["service"]), item["method"], item.get("params", {}), timeout=6)
        except Exception:
            pass

    def _nav(self, entry, event):
        if event.keyval == Gdk.KEY_Escape:
            self.hide()
            return True
        return False
