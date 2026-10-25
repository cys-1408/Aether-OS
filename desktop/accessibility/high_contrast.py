"""High contrast profile (GSettings + CSS class)."""
from __future__ import annotations

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

from shell_settings import settings


def apply(root_widget: Gtk.Widget | None = None) -> bool:
    enabled = settings().get_boolean("high-contrast")
    if root_widget is not None and enabled:
        root_widget.get_style_context().add_class("hc")
    return enabled


def set_enabled(on: bool) -> None:
    settings().set_boolean("high-contrast", on)
