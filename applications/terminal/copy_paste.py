"""Clipboard helpers: Ctrl+Shift+C / Ctrl+Shift+V for both terminal paths."""

from __future__ import annotations

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gdk, Gtk

COPY_COMBOS = ((Gdk.ModifierType.CONTROL_MASK | Gdk.ModifierType.SHIFT_MASK, Gdk.KEY_c),
               (Gdk.ModifierType.CONTROL_MASK | Gdk.ModifierType.SHIFT_MASK, Gdk.KEY_C))
PASTE_COMBOS = ((Gdk.ModifierType.CONTROL_MASK | Gdk.ModifierType.SHIFT_MASK, Gdk.KEY_v),
                (Gdk.ModifierType.CONTROL_MASK | Gdk.ModifierType.SHIFT_MASK, Gdk.KEY_V))


def matches(event: Gdk.EventKey, combos) -> bool:
    state = event.state & (Gdk.ModifierType.CONTROL_MASK | Gdk.ModifierType.SHIFT_MASK)
    return any(state == want_state and event.keyval == want_key
               for want_state, want_key in combos)


def get_selection_or_buffer_text(textview: Gtk.TextView) -> str:
    buffer = textview.get_buffer()
    bounds = buffer.get_selection_bounds()
    if bounds:
        return buffer.get_text(bounds[0], bounds[1], True)
    start, end = buffer.get_bounds()
    return buffer.get_text(start, end, True)


def copy_text(text: str) -> None:
    clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
    clipboard.set_text(text, -1)


def copy_from_view(textview: Gtk.TextView) -> bool:
    text = get_selection_or_buffer_text(textview)
    if not text:
        return False
    copy_text(text)
    return True


def paste_to_view(textview: Gtk.TextView) -> str:
    """Read the clipboard synchronously (small text; acceptable for a shell)."""
    clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
    text = clipboard.wait_for_text()
    return text or ""


def handle_copy_paste_shortcut(event: Gdk.EventKey, textview: Gtk.TextView,
                               paste_callback) -> bool:
    """Shared key handler. Returns True when the shortcut was consumed."""
    if matches(event, COPY_COMBOS):
        copy_from_view(textview)
        return True
    if matches(event, PASTE_COMBOS):
        text = paste_to_view(textview)
        if text:
            paste_callback(text)
        return True
    return False
