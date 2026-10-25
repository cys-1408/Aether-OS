"""Privacy page: real controls over consent/retention."""
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
    box.pack_start(Gtk.Label(label="Aether is local-first: no telemetry, no accounts, no cloud AI.", xalign=0), False, False, 0)
    consent = app.services.call("consent", "Consent.list", {})
    grants = (consent or {}).get("grants", {})
    box.pack_start(Gtk.Label(label=f"Network grants: {grants or 'none'}", xalign=0), False, False, 0)
    clear_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
    for label, service, method in (("Clear IntentFS index", "intentfs", "IntentFS.clear"),
                                   ("Clear action history", "ledger", "Ledger.clear"),
                                   ("Clear clipboard history", "clipboard", "Clipboard.clear")):
        b = Gtk.Button(label=label)
        b.get_style_context().add_class("soft")
        b.connect("clicked", lambda _b, s=service, m=method: app.services.call(s, m, {"scope": "all"}))
        clear_row.pack_start(b, False, False, 0)
    box.pack_start(clear_row, False, False, 0)
    note = Gtk.Label(label="Clearing the IntentFS index never deletes your files.", xalign=0)
    note.get_style_context().add_class("sub")
    box.pack_start(note, False, False, 0)
    return box
