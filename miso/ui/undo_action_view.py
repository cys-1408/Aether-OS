"""Per-entry undo actions."""
from __future__ import annotations

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk


def build_widget() -> Gtk.Widget:
    return Gtk.Label(label="Per-entry undo actions.")
