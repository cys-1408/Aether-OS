"""Font scaling via Gtk.Settings + GSettings."""
from __future__ import annotations

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

from shell_settings import settings


def apply() -> float:
    scale = settings().get_double("font-scale")
    try:
        Gtk.Settings.get_default().set_property("gtk-xft-dpi", int(96 * scale * 1024))
    except Exception:
        pass
    return scale


def set_scale(value: float) -> None:
    value = max(0.75, min(2.0, value))
    settings().set_double("font-scale", value)
    apply()
