"""Permissions view: octal + owner/group read from stat, chmod when owner."""

from __future__ import annotations

import os
import stat
from pathlib import Path

from gi.repository import Gtk

BIT_ROWS = [
    ("owner", stat.S_IRUSR, stat.S_IWUSR, stat.S_IXUSR),
    ("group", stat.S_IRGRP, stat.S_IWGRP, stat.S_IXGRP),
    ("others", stat.S_IROTH, stat.S_IWOTH, stat.S_IXOTH),
]


class FilePermissionsView(Gtk.Dialog):
    """Shows and (when the caller owns the file) edits real permission bits."""

    def __init__(self, parent, path: Path, on_applied=None) -> None:
        super().__init__(title=f"Permissions — {path.name}", transient_for=parent, modal=True)
        self.set_default_size(420, 320)
        self._path = Path(path)
        self._on_applied = on_applied

        try:
            info = self._path.stat()
        except OSError as exc:
            self._render_error(str(exc))
            return

        self._uid = info.st_uid
        self._mode = stat.S_IMODE(info.st_mode)
        can_edit = os.geteuid() == self._uid or os.geteuid() == 0

        box = self.get_content_area()
        grid = Gtk.Grid(column_spacing=12, row_spacing=8, margin=12)

        octal = f"{self._mode >> 6 & 7}{self._mode >> 3 & 7}{self._mode & 7}"
        grid.attach(Gtk.Label(label="Octal", xalign=0), 0, 0, 1, 1)
        self._octal_entry = Gtk.Entry(text=octal)
        self._octal_entry.set_sensitive(can_edit)
        self._octal_entry.set_tooltip_text(
            "" if can_edit else "Only the file owner (or root) can change permissions"
        )
        grid.attach(self._octal_entry, 1, 0, 1, 1)
        self._octal_entry.connect("changed", self._sync_from_octal)

        grid.attach(Gtk.Label(label="Owner", xalign=0), 0, 1, 1, 1)
        grid.attach(Gtk.Label(label=self._user_name(self._uid), xalign=0), 1, 1, 1, 1)
        grid.attach(Gtk.Label(label="Group", xalign=0), 0, 2, 1, 1)
        grid.attach(Gtk.Label(label=self._group_name(info.st_gid), xalign=0), 1, 2, 1, 1)

        headers = ["Read", "Write", "Execute"]
        for col, header in enumerate(headers, start=1):
            grid.attach(Gtk.Label(label=header), col, 3, 1, 1)
        self._checks = {}
        for row, (scope, r, w, x) in enumerate(BIT_ROWS, start=4):
            grid.attach(Gtk.Label(label=scope.capitalize(), xalign=0), 0, row, 1, 1)
            for col, bit in enumerate((r, w, x), start=1):
                check = Gtk.CheckButton()
                check.set_active(bool(self._mode & bit))
                check.set_sensitive(can_edit)
                check.connect("toggled", self._sync_from_checks)
                grid.attach(check, col, row, 1, 1)
                self._checks[(scope, col)] = (check, bit)

        note = Gtk.Label(xalign=0)
        note.set_line_wrap(True)
        note.get_style_context().add_class("aether-muted")
        note.set_text(
            "Editable: you own this file."
            if can_edit
            else "Read-only: this file is owned by another user. "
                 "Changing it would require administrator privileges (polkit)."
        )
        grid.attach(note, 0, 8, 4, 1)
        box.add(grid)
        self.add_button("Close", Gtk.ResponseType.CLOSE)
        if can_edit:
            self.add_button("Apply", Gtk.ResponseType.APPLY)
            self.connect("response", self._on_response)
        else:
            self.connect("response", lambda d, _r: d.destroy())
        box.show_all()

    @staticmethod
    def _user_name(uid: int) -> str:
        import pwd

        try:
            return pwd.getpwuid(uid).pw_name
        except KeyError:
            return f"uid {uid}"

    @staticmethod
    def _group_name(gid: int) -> str:
        import grp

        try:
            return grp.getgrgid(gid).gr_name
        except KeyError:
            return f"gid {gid}"

    def _render_error(self, message: str) -> None:
        label = Gtk.Label(label=f"Cannot read permissions: {message}")
        self.get_content_area().add(label)
        self.add_button("Close", Gtk.ResponseType.CLOSE)
        self.connect("response", lambda d, _r: d.destroy())
        label.show()

    def _sync_from_octal(self, entry):
        text = entry.get_text().strip()
        if len(text) == 3 and all(c in "01234567" for c in text):
            value = int(text, 8)
            self._mode = (self._mode & ~0o777) | value
            self._refresh_checks()

    def _sync_from_checks(self, _check):
        mode = 0
        for scope, col in self._checks:
            check, bit = self._checks[(scope, col)]
            if check.get_active():
                mode |= bit
        self._mode = (self._mode & ~0o777) | mode
        self._octal_entry.handler_block_by_func(self._sync_from_octal)
        self._octal_entry.set_text(
            f"{self._mode >> 6 & 7}{self._mode >> 3 & 7}{self._mode & 7}"
        )
        self._octal_entry.handler_unblock_by_func(self._sync_from_octal)

    def _refresh_checks(self):
        for key, (check, bit) in self._checks.items():
            check.handler_block_by_func(self._sync_from_checks)
            check.set_active(bool(self._mode & bit))
            check.handler_unblock_by_func(self._sync_from_checks)

    def _on_response(self, dialog, response):
        if response == Gtk.ResponseType.APPLY:
            try:
                os.chmod(self._path, self._mode)
                if self._on_applied is not None:
                    self._on_applied(self._path)
                dialog.destroy()
            except PermissionError as exc:
                self._show_apply_error(f"Permission denied: {exc}")
            except OSError as exc:
                self._show_apply_error(str(exc))
        else:
            dialog.destroy()

    def _show_apply_error(self, message: str):
        error = Gtk.MessageDialog(
            transient_for=self, modal=True, message_type=Gtk.MessageType.ERROR,
            buttons=Gtk.ButtonsType.CLOSE, text="chmod failed",
        )
        error.format_secondary_text(message)
        error.run()
        error.destroy()
