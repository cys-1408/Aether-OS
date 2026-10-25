"""Appearance page: shell toggles + font scale + high contrast."""
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

REPO_ROOT = Path(__file__).resolve().parents[2]
import sys as _sys
_sys.path.insert(0, str(REPO_ROOT / "desktop"))
from shell_settings import settings  # noqa: E402


def build_page(app) -> Gtk.Box:
    box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8, border_width=16)
    s = settings()
    rows = [("Distraction protection", "distraction-protection"),
            ("Auto-organize windows", "auto-organize"),
            ("Reduce motion", "reduced-motion"),
            ("Text-only assistant", "text-only-mode"),
            ("High contrast", "high-contrast"),
            ("Show Miso", "miso-enabled")]
    for label, key in rows:
        sw = Gtk.Switch()
        sw.set_active(s.get_boolean(key))
        sw.connect("notify::active", lambda sw_, k=key: s.set_boolean(k, sw_.get_active()))
        row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        row.pack_start(Gtk.Label(label=label, xalign=0), True, True, 0)
        row.pack_end(sw, False, False, 0)
        box.pack_start(row, False, False, 0)
    scale_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    scale_row.pack_start(Gtk.Label(label="Font scale", xalign=0), True, True, 0)
    scale = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 0.75, 2.0, 0.05)
    scale.set_value(s.get_double("font-scale"))
    scale.set_size_request(160, -1)
    scale.connect("value-changed", lambda sc: s.set_double("font-scale", sc.get_value()))
    scale_row.pack_end(scale, False, False, 0)
    box.pack_start(scale_row, False, False, 0)
    return box
