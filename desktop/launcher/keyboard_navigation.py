"""Keyboard navigation helpers for shell surfaces."""
from __future__ import annotations

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk


def bind_escape_to_hide(widget: Gtk.Widget) -> None:
    widget.add_events(Gdk.EventMask.KEY_PRESS_MASK)
    widget.connect("key-press-event", _on_key)


def _on_key(widget, event):
    if event.keyval == Gdk.KEY_Escape:
        widget.hide()
        return True
    return False


def enable_row_activation(list_box: Gtk.ListBox, run_cb) -> None:
    list_box.connect("row-activated", lambda _lb, row: run_cb(row))
