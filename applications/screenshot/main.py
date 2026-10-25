"""Aether Screenshot — grim/slurp capture of screen, region, window."""
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

from screenshot_service import capture


class ScreenshotWindow(Gtk.Box):
    def __init__(self, app):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=8, border_width=16)
        self.app = app
        self.status = Gtk.Label(label="", xalign=0)
        self.status.get_style_context().add_class("sub")
        for label, mode in (("Full screen", "full"), ("Select region", "region"), ("Current window", "window")):
            b = Gtk.Button(label=label)
            b.get_style_context().add_class("btn" if mode == "full" else "soft")
            b.connect("clicked", self._capture, mode)
            self.pack_start(b, False, False, 0)
        self.pack_start(self.status, False, False, 0)

    def _capture(self, _btn, mode):
        result = capture(mode)
        if result.get("ok"):
            self.status.set_text(f"saved: {result['file']}")
        else:
            self.status.set_text(f"capture failed: {result.get('reason')}")


class ScreenshotApp(AetherApp):
    app_id = "org.aether.Apps.Screenshot"
    title = "Screenshot"

    def build_window(self):
        win = super().build_window()
        win.set_default_size(280, 220)
        win.add(ScreenshotWindow(self))
        return win


if __name__ == "__main__":
    sys.exit(ScreenshotApp().run(sys.argv))
