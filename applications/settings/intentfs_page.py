"""IntentFS page: status, exclusions, pause/resume, reindex, clear."""
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


def build_page(app) -> Gtk.Box:
    box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8, border_width=16)
    status = app.services.call("intentfs", "IntentFS.status", {})
    if not status:
        box.pack_start(Gtk.Label(label="IntentFS unreachable — filename search still works.", xalign=0), False, False, 0)
        return box
    box.pack_start(Gtk.Label(label=str(status)[:400], xalign=0), False, False, 0)
    row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
    for label, method in (("Pause", "IntentFS.pause"), ("Resume", "IntentFS.resume"),
                          ("Reindex", "IntentFS.reindex"), ("Clear index", "IntentFS.clear")):
        b = Gtk.Button(label=label)
        b.get_style_context().add_class("soft")
        b.connect("clicked", lambda _b, m=method: app.services.call("intentfs", m, {}))
        row.pack_start(b, False, False, 0)
    box.pack_start(row, False, False, 0)
    note = Gtk.Label(label="Clearing removes only index data — original files are never touched.", xalign=0)
    note.get_style_context().add_class("sub")
    box.pack_start(note, False, False, 0)
    return box
