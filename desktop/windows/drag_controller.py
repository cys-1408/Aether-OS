"""Title-bar drag -> compositor move (never browser-style absolute coords)."""
from __future__ import annotations

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk


def make_draggable(title_bar: Gtk.Widget, window: Gtk.Window, wm=None, wid: int | None = None):
    title_bar.add_events(Gdk.EventMask.BUTTON1_MOTION_MASK | Gdk.EventMask.BUTTON_PRESS_MASK)

    def on_press(_w, event):
        if wm and wid:
            wm.adapter.run(f"[con_id={wid}] move position mouse")
        else:
            window.begin_move_drag(event.button, int(event.x_root), int(event.y_root), event.time)
    title_bar.connect("button-press-event", on_press)
