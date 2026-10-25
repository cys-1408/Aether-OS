"""Accessibility page: a11y toggles + screen reader status."""
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
from accessibility.screen_reader_bridge import initialize  # noqa: E402


def build_page(app) -> Gtk.Box:
    box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8, border_width=16)
    s = settings()
    for label, key in (("Reduce motion", "reduced-motion"), ("Text-only assistant", "text-only-mode"),
                       ("High contrast", "high-contrast")):
        sw = Gtk.Switch()
        sw.set_active(s.get_boolean(key))
        sw.connect("notify::active", lambda sw_, k=key: s.set_boolean(k, sw_.get_active()))
        row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        row.pack_start(Gtk.Label(label=label, xalign=0), True, True, 0)
        row.pack_end(sw, False, False, 0)
        box.pack_start(row, False, False, 0)
    sr = initialize()
    box.pack_start(Gtk.Label(label=str(sr), xalign=0), False, False, 0)
    return box
