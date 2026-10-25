"""Index status widget. (GTK3 widget factory)."""
from __future__ import annotations

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk


def build_widget() -> Gtk.Widget:
    return Gtk.Label(label="Index status widget. — data supplied by the Files app / settings pages")
