"""AetherApp base: identity, settings, IPC helpers, lifecycle, health."""
from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "libraries/libaether-core/python"))
DESKTOP_ROOT = REPO_ROOT / "desktop"

import gi  # noqa: E402
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gio, GLib  # noqa: E402

from aether_core.ipc import call as ipc_call  # noqa: E402
from aether_core.errors import IpcError  # noqa: E402
from aether_core import paths  # noqa: E402
from aether_core.logging_setup import configure_logging  # noqa: E402


class Services:
    """Lazy, truthful service access — degrades with real reasons."""

    def __init__(self, log):
        self.log = log

    def call(self, service: str, method: str, params: dict | None = None, timeout: float = 8.0):
        try:
            return ipc_call(paths.resolve_socket(service), method, params or {}, timeout=timeout)
        except IpcError as e:
            self.log.debug(f"{service} unreachable: {e.message}")
            return None


class AetherApp(Gtk.Application):
    app_id = "org.aether.Apps.Generic"
    title = "Aether App"

    def __init__(self):
        super().__init__(application_id=self.app_id)
        self.log = configure_logging(self.app_id.split(".")[-1].lower())
        self.services = Services(self.log)

    def do_startup(self):
        Gtk.Application.do_startup(self)
        self._load_theme_css()

    def _load_theme_css(self):
        css_file = DESKTOP_ROOT / "theme" / "widget_style.py"
        if css_file.exists():
            try:
                import importlib.util
                spec = importlib.util.spec_from_file_location("aether_widget_style", css_file)
                mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mod)
                mod.load_css()
            except Exception as e:
                self.log.info(f"theme css unavailable: {e}")

    def do_activate(self):
        self.win = self.build_window()
        self.win.set_application(self)
        self.win.show_all()
        self.on_ready()

    def build_window(self) -> Gtk.Window:
        win = Gtk.Window(title=self.title)
        win.set_default_size(470, 400)
        win.get_style_context().add_class("aether-window")
        return win

    def on_ready(self) -> None:
        pass

    # error surface helper
    def error_banner(self, box: Gtk.Box, reason: str) -> Gtk.Label:
        lbl = Gtk.Label(label=reason, xalign=0)
        lbl.set_line_wrap(True)
        lbl.get_style_context().add_class("sub")
        box.pack_start(lbl, False, False, 0)
        return lbl
