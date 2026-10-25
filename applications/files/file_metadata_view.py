"""Metadata side panel — real stat(2) values for the selected file."""

from __future__ import annotations

import os
import stat
import time
from pathlib import Path

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk


def _human(num: float) -> str:
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if abs(num) < 1024.0 or unit == "TB":
            return f"{num:.0f} {unit}" if unit == "B" else f"{num:.1f} {unit}"
        num /= 1024.0
    return f"{num:.1f} TB"


class FileMetadataView(Gtk.Box):
    """Read-only truth panel: type, size, times, inode, permissions."""

    def __init__(self) -> None:
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=6, margin=10)
        title = Gtk.Label(label="Metadata", xalign=0)
        title.get_style_context().add_class("aether-title")
        self.pack_start(title, False, False, 0)
        self._rows = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        self.pack_start(self._rows, False, False, 0)
        self._empty = Gtk.Label(label="No selection", xalign=0)
        self._empty.get_style_context().add_class("aether-muted")
        self.pack_start(self._empty, False, False, 0)
        self.set_size_request(240, -1)

    def show_file(self, path: Path) -> None:
        path = Path(path)
        for child in self._rows.get_children():
            self._rows.remove(child)
        try:
            info = path.stat()
        except OSError as exc:
            self._empty.set_text(f"Cannot stat: {exc}")
            self._empty.show()
            return
        self._empty.hide()
        mode = stat.S_IMODE(info.st_mode)
        if stat.S_ISDIR(info.st_mode):
            kind = "Directory"
        elif stat.S_ISLNK(info.st_mode):
            kind = "Symbolic link"
        else:
            kind = "Regular file"
        try:
            from gi.repository import Gio

            mime, _uncertain = Gio.content_type_guess(str(path), None, True)
        except Exception:
            mime = "unknown"
        rows = [
            ("Path", str(path)),
            ("Kind", kind),
            ("MIME", mime),
            ("Size", "—" if stat.S_ISDIR(info.st_mode) else _human(info.st_size)),
            ("Modified", time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(info.st_mtime))),
            ("Accessed", time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(info.st_atime))),
            ("Changed", time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(info.st_ctime))),
            ("Permissions", f"{stat.filemode(mode)} ({mode >> 6 & 7}{mode >> 3 & 7}{mode & 7})"),
            ("Owner", f"uid {info.st_uid} / gid {info.st_gid}"),
            ("Inode", f"{info.st_ino} on device {info.st_dev}"),
            ("Links", str(info.st_nlink)),
        ]
        for key, value in rows:
            line = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
            name = Gtk.Label(label=key, xalign=0)
            name.get_style_context().add_class("aether-muted")
            name.set_size_request(90, -1)
            val = Gtk.Label(label=value, xalign=0)
            val.set_line_wrap(True)
            val.set_selectable(True)
            line.pack_start(name, False, False, 0)
            line.pack_start(val, True, True, 0)
            self._rows.pack_start(line, False, False, 1)
        self._rows.show_all()

    def clear(self) -> None:
        for child in self._rows.get_children():
            self._rows.remove(child)
        self._empty.set_text("No selection")
        self._empty.show()
