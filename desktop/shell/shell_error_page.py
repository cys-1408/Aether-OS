"""In-shell error surface: true reason + retry (never fake success)."""
from __future__ import annotations

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk


class ShellErrorPage(Gtk.Box):
    def __init__(self, title: str, reason: str, retry_cb=None):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        self.get_style_context().add_class("card")
        t = Gtk.Label(label=title)
        t.get_style_context().add_class("h1")
        r = Gtk.Label(label=reason)
        r.set_line_wrap(True)
        r.get_style_context().add_class("sub")
        self.pack_start(t, False, False, 0)
        self.pack_start(r, False, False, 0)
        if retry_cb:
            btn = Gtk.Button(label="Retry")
            btn.get_style_context().add_class("btn")
            btn.connect("clicked", lambda _: retry_cb())
            self.pack_start(btn, False, False, 0)
