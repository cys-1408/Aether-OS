"""Aether Recovery Center — real rollback/repair/index/model recovery surfaces."""
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

from recovery_dashboard import capabilities_text
from update_rollback_view import rollback_info
from model_repair_view import repair_models
from intentfs_rebuild_view import rebuild_index
from diagnostic_export_view import export_bundle


class RecoveryWindow(Gtk.Box):
    def __init__(self, app):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=8, border_width=16)
        self.app = app
        eyebrow = Gtk.Label(label="RECOVERY", xalign=0)
        eyebrow.get_style_context().add_class("eyebrow")
        self.pack_start(eyebrow, False, False, 0)
        self.status = Gtk.Label(label=capabilities_text(app), xalign=0)
        self.status.get_style_context().add_class("sub")
        self.status.set_line_wrap(True)
        self.pack_start(self.status, False, False, 0)
        for label, cb in (("Rollback info", lambda b: self._set(rollback_info(app))),
                          ("Repair/remove broken models", self._models),
                          ("Rebuild IntentFS index", self._rebuild),
                          ("Export diagnostic bundle", self._bundle)):
            b = Gtk.Button(label=label)
            b.get_style_context().add_class("soft")
            b.connect("clicked", cb)
            self.pack_start(b, False, False, 0)
        note = Gtk.Label(label="Full offline repair tools live in the recovery boot entry.", xalign=0)
        note.get_style_context().add_class("sub")
        self.pack_start(note, False, False, 0)

    def _set(self, text):
        self.status.set_text(text)

    def _models(self, _btn):
        self._set(repair_models(self.app))

    def _rebuild(self, _btn):
        self._set(rebuild_index(self.app))

    def _bundle(self, _btn):
        self._set(export_bundle(self.app))


class RecoveryApp(AetherApp):
    app_id = "org.aether.Apps.RecoveryCenter"
    title = "Recovery Center"

    def build_window(self):
        win = super().build_window()
        win.set_default_size(420, 340)
        win.add(RecoveryWindow(self))
        return win


if __name__ == "__main__":
    sys.exit(RecoveryApp().run(sys.argv))
