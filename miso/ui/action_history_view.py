"""Action history from the ledger."""
from __future__ import annotations

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk


def build_widget() -> Gtk.Widget:
    return Gtk.Label(label="Action history from the ledger.")
