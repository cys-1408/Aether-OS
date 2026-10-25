"""Visible focus rings + full traversal policy."""
from __future__ import annotations

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk


def ensure_focus_visible(widget: Gtk.Widget) -> None:
    widget.set_focus_on_click(True)
    widget.set_can_focus(True)


def chain(widgets: list[Gtk.Widget]) -> None:
    """Set explicit focus chain for full keyboard traversal."""
    try:
        top = widgets[0].get_toplevel()
        top.set_focus_chain(widgets)
    except Exception:
        pass
