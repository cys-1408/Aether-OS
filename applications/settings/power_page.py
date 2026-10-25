"""Power page: profiles + suspend via Power.* services."""
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
    status = app.services.call("power-manager", "Power.status", {})
    if not status:
        box.pack_start(Gtk.Label(label="Power service unreachable", xalign=0), False, False, 0)
        return box
    box.pack_start(Gtk.Label(label=f"Battery: {status.get('battery', {})}", xalign=0), False, False, 0)
    box.pack_start(Gtk.Label(label=f"Thermal: {status.get('thermal', {})}", xalign=0), False, False, 0)
    row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
    for profile in status.get("profiles", []):
        b = Gtk.Button(label=profile)
        b.get_style_context().add_class("soft")
        b.connect("clicked", lambda _b, p=profile: app.services.call("power-manager", "Power.set_profile", {"profile": p}))
        row.pack_start(b, False, False, 0)
    box.pack_start(row, False, False, 0)
    suspend = Gtk.Button(label="Suspend")
    suspend.get_style_context().add_class("btn")
    suspend.connect("clicked", lambda _b: app.services.call("power-manager", "Power.suspend", {}))
    box.pack_start(suspend, False, False, 0)
    return box
