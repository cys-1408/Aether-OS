"""Trash view: list, restore and permanent delete with destructive confirm."""

from __future__ import annotations

import datetime
from pathlib import Path

from gi.repository import GLib, Gtk

(
    COL_NAME,
    COL_ORIGIN,
    COL_DATE,
    COL_RAW,
) = range(4)


class TrashView(Gtk.Box):
    """Sidebar Trash page backed by aether_core.filesops.list_trash."""

    __gsignals__ = {
        "trash-restored": (GLib.SIGNAL_RUN_FIRST, None, (str,)),
    }

    def __init__(self, parent_window: Gtk.Window, file_ops) -> None:
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=8, margin=10)
        self._parent = parent_window
        self._ops = file_ops

        header = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        title = Gtk.Label(label="Trash", xalign=0)
        title.get_style_context().add_class("aether-title")
        title.set_hexpand(True)
        refresh_btn = Gtk.Button(label="Refresh")
        refresh_btn.get_style_context().add_class("btn-soft")
        refresh_btn.connect("clicked", lambda _b: self.refresh())
        restore_btn = Gtk.Button(label="Restore")
        restore_btn.get_style_context().add_class("btn-orange")
        restore_btn.connect("clicked", self._on_restore)
        delete_btn = Gtk.Button(label="Delete permanently")
        delete_btn.get_style_context().add_class("btn-dark")
        delete_btn.connect("clicked", self._on_delete)
        header.pack_start(title, True, True, 0)
        header.pack_end(delete_btn, False, False, 0)
        header.pack_end(restore_btn, False, False, 0)
        header.pack_end(refresh_btn, False, False, 0)
        self.pack_start(header, False, False, 0)

        self._banner = Gtk.Label(xalign=0)
        self._banner.set_line_wrap(True)
        self._banner.set_no_show_all(True)
        self.pack_start(self._banner, False, False, 0)

        self.store = Gtk.ListStore(str, str, str, str)
        self.view = Gtk.TreeView(model=self.store)
        for title_text, col, width in (
            ("Name", COL_NAME, 200), ("Original location", COL_ORIGIN, 300),
            ("Deletion date", COL_DATE, 150),
        ):
            cell = Gtk.CellRendererText()
            cell.set_property("ellipsize", 3)
            column = Gtk.TreeViewColumn(title_text, cell, text=col)
            column.set_resizable(True)
            column.set_min_width(width)
            self.view.append_column(column)
        scroll = Gtk.ScrolledWindow()
        scroll.add(self.view)
        scroll.set_vexpand(True)
        self.pack_start(scroll, True, True, 0)

    def refresh(self) -> None:
        self.store.clear()
        try:
            entries = self._ops.list_trash()
        except RuntimeError as exc:
            self._banner.set_text(f"Trash service unavailable: {exc}")
            self._banner.get_style_context().add_class("aether-pill-bad")
            self._banner.show()
            return
        self._banner.hide()
        if not entries:
            self._banner.set_text("Trash is empty.")
            self._banner.get_style_context().remove_class("aether-pill-bad")
            self._banner.show()
            return
        for entry in entries:
            if not isinstance(entry, dict):
                continue
            name = str(
                entry.get("trash_name") or entry.get("name")
                or Path(str(entry.get("original_path", ""))).name or "entry"
            )
            origin = str(
                entry.get("original_path") or entry.get("path") or entry.get("origin") or "?"
            )
            raw_date = entry.get("deletion_date") or entry.get("date") or ""
            date_text = self._fmt_date(raw_date)
            self.store.append([name, origin, date_text, name])

    @staticmethod
    def _fmt_date(raw) -> str:
        if isinstance(raw, (int, float)) and raw > 0:
            return datetime.datetime.fromtimestamp(raw).strftime("%Y-%m-%d %H:%M")
        text = str(raw)
        # freedesktop trashinfo timestamps look like 2026-10-24T12:00:00
        if "T" in text:
            return text.replace("T", " ")[:16]
        return text or "?"

    def _selected(self):
        model, tree_iter = self.view.get_selection().get_selected()
        if tree_iter is None:
            return None
        return model[tree_iter]

    def _on_restore(self, _button):
        row = self._selected()
        if row is None:
            self._flash("Select a trash entry to restore.", "aether-pill-warn")
            return
        try:
            restored_to = self._ops.restore_from_trash(row[COL_RAW])
        except RuntimeError as exc:
            self._flash(f"Restore failed: {exc}", "aether-pill-bad")
            return
        self.emit("trash-restored", restored_to)
        self.refresh()

    def _on_delete(self, _button):
        row = self._selected()
        if row is None:
            self._flash("Select a trash entry to delete.", "aether-pill-warn")
            return
        confirm = Gtk.MessageDialog(
            transient_for=self._parent, modal=True,
            message_type=Gtk.MessageType.WARNING, buttons=Gtk.ButtonsType.OK_CANCEL,
            text=f"Permanently delete “{row[COL_NAME]}”?",
        )
        confirm.format_secondary_text(
            "This cannot be undone. The item will not go back to Files or Trash."
        )
        answer = confirm.run()
        confirm.destroy()
        if answer != Gtk.ResponseType.OK:
            return
        try:
            self._ops.delete_from_trash(row[COL_RAW])
        except (RuntimeError, OSError) as exc:
            self._flash(f"Delete failed: {exc}", "aether-pill-bad")
            return
        self.refresh()

    def _flash(self, message: str, css_class: str) -> None:
        self._banner.set_text(message)
        for cls in ("aether-pill-warn", "aether-pill-bad"):
            self._banner.get_style_context().remove_class(cls)
        self._banner.get_style_context().add_class(css_class)
        self._banner.show()
        GLib.timeout_add_seconds(6, self._clear_flash)

    def _clear_flash(self):
        self._banner.hide()
        return GLib.SOURCE_REMOVE
