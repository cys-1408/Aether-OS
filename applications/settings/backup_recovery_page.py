"""Backup page: targets + run/verify via Backup.* services."""
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
    status = app.services.call("backup", "Backup.status", {})
    label = Gtk.Label(label=str(status)[:400] if status else "backup service unreachable", xalign=0)
    label.get_style_context().add_class("sub")
    box.pack_start(label, False, False, 0)
    row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
    for title, method, params in (("Back up now", "Backup.run", {"target": str(__import__("pathlib").Path.home() / "Backups")}),
                                  ("Verify last", "Backup.verify", {})):
        b = Gtk.Button(label=title)
        b.get_style_context().add_class("soft")
        b.connect("clicked", lambda _b, m=method, p=params: app.services.call("backup", m, p, timeout=1800))
        row.pack_start(b, False, False, 0)
    box.pack_start(row, False, False, 0)
    return box
