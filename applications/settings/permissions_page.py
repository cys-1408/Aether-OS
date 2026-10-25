"""Permissions page: real consent grants with revoke."""
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
    consent = app.services.call("consent", "Consent.list", {})
    grants = (consent or {}).get("grants", {})
    if not grants:
        box.pack_start(Gtk.Label(label="No capability network grants.", xalign=0), False, False, 0)
    for cap, decision in grants.items():
        row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        row.pack_start(Gtk.Label(label=f"{cap}: {decision}", xalign=0), True, True, 0)
        revoke = Gtk.Button(label="Revoke")
        revoke.get_style_context().add_class("soft")
        revoke.connect("clicked", lambda _b, c=cap: app.services.call("consent", "Consent.revoke", {"capability_id": c}))
        row.pack_end(revoke, False, False, 0)
        box.pack_start(row, False, False, 0)
    return box
