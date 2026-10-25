"""Updates page: check/status/install with real confirmations."""
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


def build_page(app) -> Gtk.Box:
    box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8, border_width=16)
    label = Gtk.Label(label="checking…", xalign=0)
    label.get_style_context().add_class("sub")
    box.pack_start(label, False, False, 0)
    row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
    check = Gtk.Button(label="Check now")
    check.get_style_context().add_class("btn")
    install = Gtk.Button(label="Download & install…")
    install.get_style_context().add_class("soft")
    row.pack_start(check, False, False, 0)
    row.pack_start(install, False, False, 0)
    box.pack_start(row, False, False, 0)

    def do_check(_btn):
        data = app.services.call("updates", "Updates.check", {}, timeout=60)
        if data:
            GLib.idle_add(label.set_text, f"status: {data.get('status', 'unknown')} · {data.get('summary', '')}")
        else:
            GLib.idle_add(label.set_text, "update service unreachable")

    def do_install(_btn):
        dlg = Gtk.MessageDialog(text="Install updates?", secondary_text="This runs a real package transaction and keeps a known-good rollback entry.",
                                buttons=Gtk.ButtonsType.OK_CANCEL)
        if dlg.run() == Gtk.ResponseType.OK:
            app.services.call("updates", "Updates.install", {}, timeout=1800)
            GLib.idle_add(label.set_text, "install finished — see Recovery Center for rollback options")
        dlg.destroy()

    check.connect("clicked", do_check)
    install.connect("clicked", do_install)
    return box
