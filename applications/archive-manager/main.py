"""Aether Archive Manager — safe zip/tar extract & create (traversal-guarded)."""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[2]
for p in (REPO_ROOT / "libraries/libaether-core/python", REPO_ROOT / "applications/app-framework"):
    sys.path.insert(0, str(p))

from application_context import AetherApp  # noqa: E402

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

from archive_browser import list_archive
from archive_extract import extract
from archive_create import create


class ArchiveWindow(Gtk.Box):
    def __init__(self, app):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=8, border_width=14)
        self.app = app
        self.archive_path = None
        bar = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        open_btn = Gtk.Button(label="Open archive")
        open_btn.get_style_context().add_class("btn")
        open_btn.connect("clicked", self._open)
        bar.pack_start(open_btn, False, False, 0)
        extract_btn = Gtk.Button(label="Extract…")
        extract_btn.get_style_context().add_class("soft")
        extract_btn.connect("clicked", self._extract)
        bar.pack_start(extract_btn, False, False, 0)
        create_btn = Gtk.Button(label="Create…")
        create_btn.get_style_context().add_class("soft")
        create_btn.connect("clicked", self._create)
        bar.pack_start(create_btn, False, False, 0)
        self.pack_start(bar, False, False, 0)
        self.status = Gtk.Label(label="zip · tar · tar.gz · tar.bz2 · tar.xz", xalign=0)
        self.status.get_style_context().add_class("sub")
        self.pack_start(self.status, False, False, 0)
        self.model = Gtk.ListStore(str, int)
        self.tree = Gtk.TreeView(model=self.model)
        for i, title in enumerate(("Member", "Size")):
            self.tree.append_column(Gtk.TreeViewColumn(title, Gtk.CellRendererText(), text=i))
        scroll = Gtk.ScrolledWindow()
        scroll.set_vexpand(True)
        scroll.add(self.tree)
        self.pack_start(scroll, True, True, 0)

    def _open(self, _btn):
        from desktop.dialogs.file_picker_adapter import choose_file
        path = choose_file(self.get_toplevel(), "Open archive")
        if path:
            self.archive_path = path
            self.model.clear()
            try:
                for name, size in list_archive(path)[:500]:
                    self.model.append([name, size])
                self.status.set_text(f"{path}")
            except Exception as e:
                self.status.set_text(f"cannot read archive: {e}")

    def _extract(self, _btn):
        if not self.archive_path:
            return
        from desktop.dialogs.file_picker_adapter import choose_folder
        dest = choose_folder(self.get_toplevel(), "Extract to")
        if dest:
            try:
                result = extract(self.archive_path, dest)
                self.status.set_text(f"extracted {result['extracted']} files to {dest}")
            except Exception as e:
                self.status.set_text(f"extract failed: {e}")

    def _create(self, _btn):
        from desktop.dialogs.file_picker_adapter import choose_file
        path = choose_file(self.get_toplevel(), "New archive (zip or tar.gz)", save=True)
        if not path:
            return
        from desktop.dialogs.file_picker_adapter import choose_file as cf
        members = []
        while True:
            f = cf(self.get_toplevel(), "Add file to archive")
            if not f:
                break
            members.append(f)
        try:
            result = create(path, members)
            self.status.set_text(f"created {result['archive']} with {result['members']} files")
        except Exception as e:
            self.status.set_text(f"create failed: {e}")


class ArchiveApp(AetherApp):
    app_id = "org.aether.Apps.ArchiveManager"
    title = "Archive Manager"

    def build_window(self):
        win = super().build_window()
        win.set_default_size(460, 380)
        win.add(ArchiveWindow(self))
        return win


if __name__ == "__main__":
    sys.exit(ArchiveApp().run(sys.argv))
