"""Aether Focus — real sessions wired to the shell focus controller."""
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
from gi.repository import Gtk

from focus_session import FocusSession


class FocusWindow(Gtk.Box):
    def __init__(self, app):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=8, border_width=16)
        self.app = app
        eyebrow = Gtk.Label(label="ONE THING AT A TIME", xalign=0)
        eyebrow.get_style_context().add_class("eyebrow")
        self.pack_start(eyebrow, False, False, 0)

        self.session = FocusSession(app)
        self.display = Gtk.Label(label="25:00")
        self.display.get_style_context().add_class("h1")
        self.pack_start(self.display, False, False, 0)

        row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        self.durations = Gtk.ComboBoxText()
        for m in ("5 minute break", "15 minutes", "25 minutes", "45 minutes", "60 minutes"):
            self.durations.append_text(m)
        self.durations.set_active(2)
        row.pack_start(self.durations, False, False, 0)
        start = Gtk.Button(label="Start")
        start.get_style_context().add_class("btn-orange")
        start.connect("clicked", self._start)
        row.pack_start(start, False, False, 0)
        reset = Gtk.Button(label="Reset")
        reset.get_style_context().add_class("soft")
        reset.connect("clicked", self._reset)
        row.pack_start(reset, False, False, 0)
        self.pack_start(row, False, False, 0)

        note = Gtk.Label(label="Start runs a real focus session — other windows dim, "
                               "Miso keeps watch. Shell control is used when available.",
                         xalign=0)
        note.set_line_wrap(True)
        note.get_style_context().add_class("sub")
        self.pack_start(note, False, False, 0)

        GLib = __import__("gi.repository", fromlist=["GLib"]).GLib
        GLib.timeout_add_seconds(1, self._tick)

    def _start(self, _btn):
        minutes = int(self.durations.get_active_text().split()[0])
        self.session.start(minutes)
        self._reset_display(minutes)

    def _reset(self, _btn):
        self.session.reset()
        self._reset_display(int(self.durations.get_active_text().split()[0]))

    def _reset_display(self, minutes):
        self.display.set_text(f"{minutes:02d}:00")

    def _tick(self):
        self.display.set_text(self.session.render())
        return True


class FocusApp(AetherApp):
    app_id = "org.aether.Apps.Focus"
    title = "Focus timer"

    def build_window(self):
        win = super().build_window()
        win.set_default_size(300, 320)
        win.add(FocusWindow(self))
        return win


if __name__ == "__main__":
    sys.exit(FocusApp().run(sys.argv))
