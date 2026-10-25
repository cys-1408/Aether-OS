"""Display page: real output modes/scale via compositor adapter."""
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
from compositor.display_manager import outputs, set_mode, set_scale  # noqa: E402


def build_page(app) -> Gtk.Box:
    box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8, border_width=16)
    outs = outputs()
    if not outs:
        box.pack_start(Gtk.Label(label="No compositor session detected (display controls need the desktop session).",
                                 xalign=0), False, False, 0)
        return box
    for out in outs:
        name = out.get("name", "?")
        row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        row.pack_start(Gtk.Label(label=name, xalign=0), False, False, 0)
        combo = Gtk.ComboBoxText()
        for mode in (out.get("modes") or [])[:1]:
            combo.append_text(str(mode.get("name", "")))
        scale = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 0.5, 3.0, 0.25)
        scale.set_size_request(120, -1)
        scale.set_value(out.get("scale") or 1.0)
        scale.connect("value-changed", lambda sc, n=name: set_scale(n, sc.get_value()))
        row.pack_start(combo, False, False, 0)
        row.pack_end(scale, False, False, 0)
        box.pack_start(row, False, False, 0)
    return box
