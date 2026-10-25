"""Aether Clock — live time, world clocks, timer, reminders."""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[2]
for p in (REPO_ROOT / "libraries/libaether-core/python", REPO_ROOT / "applications/app-framework"):
    sys.path.insert(0, str(p))

from application_context import AetherApp  # noqa: E402

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GLib

from timezone_view import world_clocks
from timer_view import TimerView


class ClockWindow(Gtk.Box):
    def __init__(self, app):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=8, border_width=16)
        self.app = app
        eyebrow = Gtk.Label(label="WALL CLOCK", xalign=0)
        eyebrow.get_style_context().add_class("eyebrow")
        self.pack_start(eyebrow, False, False, 0)
        self.time_lbl = Gtk.Label(label="--:--:--")
        self.time_lbl.get_style_context().add_class("h1")
        self.pack_start(self.time_lbl, False, False, 0)
        self.date_lbl = Gtk.Label(label="")
        self.date_lbl.get_style_context().add_class("sub")
        self.pack_start(self.date_lbl, False, False, 0)

        self.world = Gtk.Label(label="", xalign=0)
        self.world.get_style_context().add_class("sub")
        self.pack_start(self.world, False, False, 0)

        self.pack_start(Gtk.Separator(), False, False, 4)
        timer_lbl = Gtk.Label(label="Timer", xalign=0)
        timer_lbl.get_style_context().add_class("eyebrow")
        self.pack_start(timer_lbl, False, False, 0)
        self.pack_start(TimerView(app), True, True, 0)

        self._tick()
        GLib.timeout_add_seconds(1, self._tick)

    def _tick(self):
        from gi.repository import GLib as g
        now = g.DateTime.new_now_local()
        self.time_lbl.set_text(now.format("%H:%M:%S"))
        self.date_lbl.set_text(now.format("%A, %B %-d, %Y"))
        self.world.set_text(world_clocks())
        return True


class ClockApp(AetherApp):
    app_id = "org.aether.Apps.Clock"
    title = "Clock"

    def build_window(self):
        win = super().build_window()
        win.set_default_size(320, 340)
        win.add(ClockWindow(self))
        return win


if __name__ == "__main__":
    sys.exit(ClockApp().run(sys.argv))
