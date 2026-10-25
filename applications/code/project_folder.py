"""Project folder tree: lazy Gtk.TreeStore over the real filesystem."""

from __future__ import annotations

import os
from pathlib import Path

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import GLib, Gtk

(
    COL_PATH,
    COL_NAME,
    COL_IS_DIR,
) = range(3)


class ProjectTree(Gtk.Box):
    """Directory browser with lazy expansion; emits file-activated."""

    __gsignals__ = {
        "file-activated": (GLib.SIGNAL_RUN_FIRST, None, (str,)),
    }

    def __init__(self) -> None:
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        self.set_size_request(230, -1)
        self.get_style_context().add_class("sidebar")

        header = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=4, margin=4)
        self._root_label = Gtk.Label(label="No folder open", xalign=0)
        self._root_label.set_ellipsize(3)
        self._root_label.get_style_context().add_class("aether-muted")
        open_btn = Gtk.Button(label="Open…")
        open_btn.set_relief(Gtk.ReliefStyle.NONE)
        open_btn.connect("clicked", self._choose_root)
        refresh_btn = Gtk.Button(label="⟳")
        refresh_btn.set_relief(Gtk.ReliefStyle.NONE)
        refresh_btn.connect("clicked", lambda _b: self.set_root(self.root))
        header.pack_start(self._root_label, True, True, 0)
        header.pack_end(refresh_btn, False, False, 0)
        header.pack_end(open_btn, False, False, 0)
        self.pack_start(header, False, False, 0)

        self.store = Gtk.TreeStore(str, str, bool)
        self.view = Gtk.TreeView(model=self.store)
        self.view.set_headers_visible(False)
        cell = Gtk.CellRendererText()
        cell.set_property("ellipsize", 3)
        column = Gtk.TreeViewColumn("", cell, text=COL_NAME)
        self.view.append_column(column)
        self.view.connect("row-expanded", self._on_row_expanded)
        self.view.connect("row-activated", self._on_row_activated)
        scroll = Gtk.ScrolledWindow()
        scroll.add(self.view)
        self.pack_start(scroll, True, True, 0)
        self.root: Path | None = None
        self._expanded_once = set()

    def set_root(self, directory) -> None:
        directory = Path(directory) if directory else None
        self.store.clear()
        self._expanded_once.clear()
        if directory is None or not directory.is_dir():
            self._root_label.set_text("No folder open")
            self.root = None
            return
        self.root = directory
        self._root_label.set_text(directory.name)
        self._insert_children(None, directory)

    def _choose_root(self, _button):
        chooser = Gtk.FileChooserDialog(
            title="Open project folder", transient_for=self.get_toplevel(),
            action=Gtk.FileChooserAction.SELECT_FOLDER,
            buttons=("Cancel", Gtk.ResponseType.CANCEL, "Open", Gtk.ResponseType.OK),
        )
        answer = chooser.run()
        chosen = chooser.get_filename()
        chooser.destroy()
        if answer == Gtk.ResponseType.OK and chosen:
            self.set_root(chosen)

    def _insert_children(self, parent_iter, directory: Path) -> None:
        try:
            entries = sorted(
                os.scandir(directory),
                key=lambda e: (not e.is_dir(), e.name.lower()),
            )
        except OSError as exc:
            self.store.append(parent_iter, ["", f"(unreadable: {exc})", False])
            return
        for entry in entries:
            name = entry.name
            if name.startswith("."):
                continue
            try:
                is_dir = entry.is_dir(follow_symlinks=False)
            except OSError:
                is_dir = False
            tree_iter = self.store.append(
                parent_iter, [str(entry.path), name, is_dir]
            )
            if is_dir:
                self.store.append(tree_iter, ["", "", True])  # expand placeholder

    def _on_row_expanded(self, _view, tree_iter, _path):
        marker = str(self.store[tree_iter][COL_PATH])
        if marker in self._expanded_once:
            return
        self._expanded_once.add(marker)
        child = self.store.iter_children(tree_iter)
        if child is not None and self.store[child][COL_PATH] == "" and not self.store[child][COL_NAME]:
            self.store.remove(child)
        directory = Path(self.store[tree_iter][COL_PATH])
        self._insert_children(tree_iter, directory)

    def _on_row_activated(self, _view, path, _column):
        row = self.store[path]
        target = row[COL_PATH]
        if not target:
            return
        if row[COL_IS_DIR]:
            self.view.expand_row(Gtk.TreePath(path), False)
        else:
            self.emit("file-activated", target)
