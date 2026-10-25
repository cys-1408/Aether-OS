"""Timer with real GLib countdown + notification on completion."""
from __future__ import annotations

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GLib


class TimerView(Gtk.Box):
    def __init__(self, app):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.app = app
        self.remaining = 0
        self.running = False
        self.display = Gtk.Label(label="00:00")
        self.display.get_style_context().add_class("h1")
        self.pack_start(self.display, False, False, 0)
        row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        self.spin = Gtk.SpinButton.new_with_range(1, 180, 1)
        self.spin.set_value(5)
        row.pack_start(self.spin, False, False, 0)
        start = Gtk.Button(label="Start")
        start.get_style_context().add_class("btn")
        start.connect("clicked", self._start)
        row.pack_start(start, False, False, 0)
        self.pack_start(row, False, False, 0)

    def _start(self, _btn):
        if self.running:
            return
        self.remaining = int(self.spin.get_value()) * 60
        self.running = True
        GLib.timeout_add_seconds(1, self._tick)

    def _tick(self):
        if not self.running:
            return False
        self.remaining -= 1
        m, s = divmod(max(0, self.remaining), 60)
        self.display.set_text(f"{m:02d}:{s:02d}")
        if self.remaining <= 0:
            self.running = False
            self.app.services.call("notifications", "Notify.notify",
                                   {"source": "clock", "category": "reminder",
                                    "title": "Timer done", "body": "Your timer finished."})
            return False
        return True
