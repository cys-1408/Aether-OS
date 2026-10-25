"""Aether Mines — real playable minesweeper with accessible controls."""
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
from gi.repository import Gtk, Gdk

from game_state import MinesGame
from game_logic import cell_label


class MinesWindow(Gtk.Box):
    def __init__(self, app):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=8, border_width=14)
        self.app = app
        self.game = MinesGame(10, 10, 8)
        eyebrow = Gtk.Label(label="MINES · click to reveal · right-click to flag", xalign=0)
        eyebrow.get_style_context().add_class("eyebrow")
        self.pack_start(eyebrow, False, False, 0)
        row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        self.stat = Gtk.Label(label="10×10 · 8 mines", xalign=0)
        self.stat.get_style_context().add_class("sub")
        self.timer_lbl = Gtk.Label(label="00:00", xalign=1)
        self.timer_lbl.get_style_context().add_class("sub")
        new_btn = Gtk.Button(label="New game")
        new_btn.get_style_context().add_class("soft")
        new_btn.connect("clicked", lambda _b: self._reset())
        row.pack_start(self.stat, False, False, 0)
        row.pack_end(self.timer_lbl, False, False, 0)
        self.pack_start(row, False, False, 0)

        self.grid = Gtk.Grid(column_homogeneous=True, row_homogeneous=True,
                             column_spacing=3, row_spacing=3)
        self.cells: list[Gtk.Button] = []
        for i in range(100):
            b = Gtk.Button(label="")
            b.set_size_request(26, 26)
            b.get_style_context().add_class("mcell")
            b.connect("clicked", self._reveal, i)
            b.connect("button-press-event", self._flag_event, i)
            b.set_tooltip_text(f"cell {i}")
            self.grid.attach(b, i % 10, i // 10, 1, 1)
            self.cells.append(b)
        self.pack_start(self.grid, True, True, 0)
        self.msg = Gtk.Label(label="", xalign=0)
        self.msg.get_style_context().add_class("sub")
        self.pack_start(self.msg, False, False, 0)
        GLib = __import__("gi.repository", fromlist=["GLib"]).GLib
        GLib.timeout_add_seconds(1, self._tick)
        self._sync()

    def _reset(self):
        self.game = MinesGame(10, 10, 8)
        self.msg.set_text("")
        self._sync()

    def _reveal(self, _btn, i):
        events = self.game.reveal(i)
        for ev in events:
            if ev["type"] == "boom":
                self.msg.set_text("Stepped on a mine. Try again?")
            elif ev["type"] == "win":
                self.msg.set_text("Cleared! Nice paw-work.")
        self._sync()

    def _flag_event(self, btn, event, i):
        if event.button == 3:
            self.game.toggle_flag(i)
            self._sync()
            return True
        return False

    def _tick(self):
        self.timer_lbl.set_text(f"{self.game.elapsed():02d}s" if self.game.started else "00:00")
        return True

    def _sync(self):
        for i, btn in enumerate(self.cells):
            state, n = self.game.cell_state(i)
            lbl, cls = cell_label(state, n)
            btn.set_label(lbl)
            ctx = btn.get_style_context()
            for c in ("rev", "mine", "n1", "n2", "n3", "flagged"):
                ctx.remove_class(c)
            if cls:
                ctx.add_class(cls)
            from game_logic import accessible_name
            btn.get_accessible().set_name(accessible_name(i, state, n))


class MinesApp(AetherApp):
    app_id = "org.aether.Apps.Mines"
    title = "Mines"

    def build_window(self):
        win = super().build_window()
        win.set_default_size(340, 420)
        win.add(MinesWindow(self))
        return win


if __name__ == "__main__":
    sys.exit(MinesApp().run(sys.argv))
