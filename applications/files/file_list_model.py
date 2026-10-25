"""File list model for Aether Files — real directory scanning with os.scandir."""

from __future__ import annotations

import grp
import os
import pwd
import stat
import time
from pathlib import Path

from gi.repository import GLib, Gtk

#: Column ids for the underlying ListStore.
(
    COL_PATH,
    COL_NAME,
    COL_IS_DIR,
    COL_SIZE,
    COL_SIZE_STR,
    COL_MTIME,
    COL_MTIME_STR,
    COL_PERMS,
    COL_OWNER,
    COL_GROUP,
    COL_KIND,
) = range(11)


def _fmt_size(num: float) -> str:
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if abs(num) < 1024.0 or unit == "TB":
            if unit == "B":
                return f"{int(num)} {unit}"
            return f"{num:.1f} {unit}"
        num /= 1024.0
    return f"{num:.1f} TB"


def _owner_name(uid: int) -> str:
    try:
        return pwd.getpwuid(uid).pw_name
    except KeyError:
        return str(uid)


def _group_name(gid: int) -> str:
    try:
        return grp.getgrgid(gid).pw_name if hasattr(grp, "getgrgid") else str(gid)
    except KeyError:
        return str(gid)


def format_mode(mode: int) -> str:
    return stat.filemode(mode)


class FileListModel:
    """Wraps a Gtk.ListStore + TreeModelSort with real filesystem contents."""

    def __init__(self) -> None:
        self.store = Gtk.ListStore(str, str, bool, int, str, int, str, str, str, str, str)
        self.sorted_model = Gtk.TreeModelSort(model=self.store)
        self.sorted_model.set_sort_func(
            COL_NAME, self._sort_by(key=COL_NAME, dirs_first=True)
        )
        self.sorted_model.set_sort_func(COL_SIZE, self._sort_by(key=COL_SIZE))
        self.sorted_model.set_sort_func(COL_MTIME, self._sort_by(key=COL_MTIME))
        self.sorted_model.set_sort_column_id(COL_NAME, Gtk.SortType.ASCENDING)

    @staticmethod
    def _sort_by(key: int, dirs_first: bool = False):
        def sorter(model, a, b, _user_data):
            if dirs_first:
                ad = model[a][COL_IS_DIR]
                bd = model[b][COL_IS_DIR]
                if ad != bd:
                    return -1 if ad else 1
            va, vb = model[a][key], model[b][key]
            na, nb = str(va).lower(), str(vb).lower()
            if na < nb:
                return -1
            if na > nb:
                return 1
            return 0

        return sorter

    def clear(self) -> None:
        self.store.clear()

    def populate(self, directory: Path, show_hidden: bool = False) -> dict:
        """Fill the model with real entries. Returns a status dict (honest)."""
        self.store.clear()
        directory = Path(directory)
        try:
            entries = list(os.scandir(directory))
        except FileNotFoundError:
            return {"ok": False, "error": f"Folder does not exist: {directory}"}
        except PermissionError:
            return {"ok": False, "error": f"Permission denied: {directory}"}
        except OSError as exc:
            return {"ok": False, "error": f"Cannot read {directory}: {exc}"}

        shown = 0
        for entry in entries:
            name = entry.name
            if not show_hidden and name.startswith("."):
                continue
            try:
                info = entry.stat(follow_symlinks=False)
            except OSError:
                continue
            is_dir = stat.S_ISDIR(info.st_mode)
            size = 0 if is_dir else info.st_size
            try:
                perms = stat.filemode(info.st_mode)
            except Exception:
                perms = "??????????"
            self.store.append(
                [
                    str(entry.path),
                    name,
                    is_dir,
                    size,
                    "<folder>" if is_dir else _fmt_size(size),
                    int(info.st_mtime),
                    time.strftime("%Y-%m-%d %H:%M", time.localtime(info.st_mtime)),
                    perms,
                    _owner_name(info.st_uid),
                    _group_name(info.st_gid),
                    "Folder" if is_dir else (Path(name).suffix.lstrip(".").upper() or "File"),
                ]
            )
            shown += 1
        return {"ok": True, "count": shown}

    def append_error_row(self, message: str) -> None:
        """Make errors visible inside the list itself (never silently blank)."""
        self.store.append(["", message, False, 0, "", 0, "", "", "", "", ""])

    def append_placeholder(self, message: str) -> None:
        GLib.idle_add(self.append_error_row, message)
