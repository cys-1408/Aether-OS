"""Aether Calculator — safe shunting-yard evaluation (NO eval)."""
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

from expression_parser import evaluate
from history_model import HistoryModel


class CalcWindow(Gtk.Box):
    def __init__(self, app):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=8, border_width=14)
        self.app = app
        self.history = HistoryModel()
        self.expr = ""
        self.display = Gtk.Label(label="0", xalign=1.0)
        self.display.get_style_context().add_class("calc-display")
        self.display.set_hexpand(True)
        self.pack_start(self.display, False, False, 0)

        grid = Gtk.Grid(row_spacing=6, column_spacing=6, column_homogeneous=True)
        keys = [["C", "(", ")", "⌫"],
                ["7", "8", "9", "÷"],
                ["4", "5", "6", "×"],
                ["1", "2", "3", "−"],
                ["0", ".", "+", "="]]
        for r, row in enumerate(keys):
            for c, k in enumerate(row):
                b = Gtk.Button(label=k)
                b.get_style_context().add_class("eq" if k == "=" else "soft")
                b.connect("clicked", self._press, k)
                grid.attach(b, c, r, 1, 1)
        self.pack_start(grid, True, True, 0)
        self.history_lbl = Gtk.Label(label="", xalign=0)
        self.history_lbl.get_style_context().add_class("sub")
        self.pack_start(self.history_lbl, False, False, 0)

        self._key_cid = self.connect("key-press-event", self._on_key)
        self.set_can_focus(True)

    def _press(self, _btn, k):
        if k == "C":
            self.expr = ""
        elif k == "⌫":
            self.expr = self.expr[:-1]
        elif k == "=":
            if not self.expr:
                return
            try:
                result = evaluate(self.expr)
                self.history.add(f"{self.expr} = {result}")
                self.expr = str(result)
            except ValueError as e:
                self._flash(f"didn't compute: {e}")
                self.expr = ""
        else:
            self.expr += k
        self.display.set_text(self.expr or "0")
        self.history_lbl.set_text(" · ".join(self.history.recent(3)))

    def _flash(self, msg):
        self.display.set_text(msg)

    def _on_key(self, _w, event):
        import Gdk
        key = Gdk.keyval_name(event.keyval)
        if key and (key.isdigit() or key in (".", "+", "-", "*", "/")):
            self._press(None, {"*": "×", "/": "÷", "-": "−"}.get(key, key))
            return True
        if event.keyval == Gdk.KEY_Return or event.keyval == Gdk.KEY_KP_Enter:
            self._press(None, "=")
            return True
        if event.keyval == Gdk.KEY_BackSpace:
            self._press(None, "⌫")
            return True
        if event.keyval == Gdk.KEY_Escape:
            self._press(None, "C")
            return True
        return False


class CalcApp(AetherApp):
    app_id = "org.aether.Apps.Calculator"
    title = "Calc"

    def build_window(self):
        win = super().build_window()
        win.set_default_size(300, 360)
        win.add(CalcWindow(self))
        return win


if __name__ == "__main__":
    sys.exit(CalcApp().run(sys.argv))
