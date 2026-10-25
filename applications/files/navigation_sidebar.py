"""Navigation sidebar: fixed places, Trash and real mounted drives."""

from __future__ import annotations

import os
from pathlib import Path

from gi.repository import GLib, Gtk

PLACE = "place"
TRASH = "trash"
DRIVE = "drive"


def _xdg_dir(name: str) -> Path:
    configured = os.environ.get(f"XDG_{name.upper()}_DIR")
    if configured:
        return Path(configured).expanduser()
    return Path.home() / name


class NavigationSidebar(Gtk.Box):
    """Places list + mounted drives from Storage.list (honest when absent)."""

    __gsignals__ = {
        "location-activated": (GLib.SIGNAL_RUN_FIRST, None, (str, str, str)),
    }

    def __init__(self, services) -> None:
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.get_style_context().add_class("sidebar")
        self.set_size_request(180, -1)
        self._services = services

        self.store = Gtk.TreeStore(str, str, str)  # kind, label, target
        self.view = Gtk.TreeView(model=self.store)
        self.view.set_headers_visible(False)
        cell = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn("", cell, text=1)
        column.set_expand(True)
        self.view.append_column(column)
        self.view.connect("row-activated", self._on_activated)

        scroll = Gtk.ScrolledWindow()
        scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scroll.add(self.view)
        self.pack_start(scroll, True, True, 0)

        self._status = Gtk.Label(label="", xalign=0)
        self._status.get_style_context().add_class("aether-muted")
        self._status.set_margin_start(10)
        self._status.set_margin_bottom(6)
        self._status.set_line_wrap(True)
        self.pack_end(self._status, False, False, 2)

        self._fill_places()

    def _fill_places(self) -> None:
        home = Path.home()
        places = [
            (PLACE, "Home", str(home)),
            (PLACE, "Documents", str(_xdg_dir("documents"))),
            (PLACE, "Downloads", str(_xdg_dir("downloads"))),
            (PLACE, "Pictures", str(_xdg_dir("pictures"))),
            (PLACE, "Music", str(_xdg_dir("music"))),
            (PLACE, "Videos", str(_xdg_dir("videos"))),
            (TRASH, "Trash", "trash://"),
        ]
        for kind, label, target in places:
            self.store.append(None, [kind, label, target])

    def refresh_drives(self) -> None:
        """Query Storage.list and add one row per real mount."""

        def on_result(result):
            self._remove_kind(DRIVE)
            mounts = result.get("mounts") if isinstance(result, dict) else None
            if not isinstance(mounts, list) or not mounts:
                self._status.set_text("No mounted drives reported by Storage service")
                return
            self._status.set_text("")
            for mount in mounts:
                target = str(mount.get("mount_point") or mount.get("target") or "")
                label = str(mount.get("label") or mount.get("device") or target or "Drive")
                if not target:
                    continue
                self.store.append(None, [DRIVE, label, target])

        def on_error(error):
            self._remove_kind(DRIVE)
            self._status.set_text(f"Drives unavailable: {error}")

        self._services.call_async("Storage", "list", {}, on_result, on_error, timeout=5.0)

    def _remove_kind(self, kind: str) -> None:
        for row in list(self.store):
            if row[0] == kind:
                self.store.remove(self.store.get_iter(row.path))

    def _on_activated(self, _view, path, _column):
        row = self.store[path]
        kind, _label, target = row[0], row[1], row[2]
        self.emit("location-activated", kind, target, _label)
