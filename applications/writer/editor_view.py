"""Editor view: styled Gtk.TextView matching the reference .note field."""

from __future__ import annotations

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk


class EditorView(Gtk.Box):
    """The writing surface plus a live status line (words / cursor / save state)."""

    def __init__(self, on_change=None) -> None:
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self._on_change = on_change
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_vexpand(True)
        self._view = Gtk.TextView()
        self._view.set_wrap_mode(Gtk.WrapMode.WORD_CHAR)
        self._view.set_left_margin(24)
        self._view.set_right_margin(24)
        self._view.set_top_margin(16)
        self._view.set_bottom_margin(16)
        self._view.get_buffer().connect("changed", self._on_buffer_changed)
        self._view.get_buffer().connect("notify::cursor-position", self._on_cursor_moved)
        scrolled.add(self._view)
        self.pack_start(scrolled, True, True, 0)

        self._status = Gtk.Label(xalign=0)
        self._status.get_style_context().add_class("aether-muted")
        self.pack_start(self._status, False, False, 0)

        context = self._view.get_style_context()
        context.add_class("aether-card")
        self._status_line = ""
        self._update_status("Ready")

    # -- buffer access ----------------------------------------------------------

    @property
    def buffer(self):
        return self._view.get_buffer()

    def set_text(self, text: str) -> None:
        self.buffer.set_text(text)
        self._update_status("Loaded")

    def get_text(self) -> str:
        start, end = self.buffer.get_bounds()
        return self.buffer.get_text(start, end, True)

    def insert_at_cursor(self, text: str) -> None:
        self.buffer.insert_at_cursor(text)

    def grab_focus_to_editor(self) -> None:
        self._view.grab_focus()

    def cursor_position(self) -> int:
        mark = self.buffer.get_insert()
        return self.buffer.get_iter_at_mark(mark).get_offset()

    # -- status -------------------------------------------------------------------

    def _on_buffer_changed(self, _buffer):
        if self._on_change is not None:
            self._on_change()
        self._update_status(self._status_line or "Edited")

    def _on_cursor_moved(self, *_args):
        self._update_status(self._status_line)

    def set_status_line(self, text: str) -> None:
        """External status (e.g. 'Saved draft 14:02') shown with live counters."""
        self._status_line = text
        self._update_status(text)

    def _update_status(self, prefix: str):
        start, end = self.buffer.get_bounds()
        text = self.buffer.get_text(start, end, True)
        words = len(text.split())
        chars = len(text)
        line_no = self.buffer.get_iter_at_mark(self.buffer.get_insert()).get_line() + 1
        parts = [f"Line {line_no} · {words} words · {chars} chars"]
        if prefix:
            parts.insert(0, prefix)
        self._status.set_text(" — ".join(parts))
