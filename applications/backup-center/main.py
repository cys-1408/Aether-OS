"""Aether Backup Center — real backups, verify, restore wizard."""
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
from gi.repository import Gtk, GLib

from backup_dashboard import status_text
from backup_targets import choose_target
from restore_wizard import run_restore_wizard
from backup_status import verify_last


class BackupWindow(Gtk.Box):
    def __init__(self, app):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=8, border_width=16)
        self.app = app
        eyebrow = Gtk.Label(label="BACKUP & RESTORE", xalign=0)
        eyebrow.get_style_context().add_class("eyebrow")
        self.pack_start(eyebrow, False, False, 0)
        self.status = Gtk.Label(label="loading…", xalign=0)
        self.status.get_style_context().add_class("sub")
        self.status.set_line_wrap(True)
        self.pack_start(self.status, False, False, 0)
        row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        for label, cb in (("Choose target…", self._target), ("Back up now", self._backup),
                          ("Verify", self._verify), ("Restore…", self._restore)):
            b = Gtk.Button(label=label)
            b.get_style_context().add_class("btn" if label == "Back up now" else "soft")
            b.connect("clicked", cb)
            row.pack_start(b, False, False, 0)
        self.pack_start(row, False, False, 0)
        self._refresh()

    def _refresh(self):
        self.status.set_text(status_text(self.app))

    def _target(self, _btn):
        choose_target(self.app)

    def _backup(self, _btn):
        target = choose_target(self.app, silent=True) or str(__import__("pathlib").Path.home() / "Backups")
        result = self.app.services.call("backup", "Backup.run", {"target": target}, timeout=3600)
        self.status.set_text(str(result))
        self._refresh()

    def _verify(self, _btn):
        self.status.set_text(verify_last(self.app))

    def _restore(self, _btn):
        run_restore_wizard(self.app, self.get_toplevel())


class BackupApp(AetherApp):
    app_id = "org.aether.Apps.BackupCenter"
    title = "Backup Center"

    def build_window(self):
        win = super().build_window()
        win.set_default_size(420, 300)
        win.add(BackupWindow(self))
        return win


if __name__ == "__main__":
    sys.exit(BackupApp().run(sys.argv))
