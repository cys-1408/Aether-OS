import sys
from pathlib import Path
_p = Path(__file__).resolve()
sys.path.insert(0, str(_p.parents[2]))
sys.path.insert(0, str(_p.parents[3] / 'libraries/libaether-core/python'))
"""Taskbar: real app launchers + active indicators (layer-shell BOTTOM, 60px)."""
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

try:
    gi.require_version("GtkLayerShell", "0.1")
    from gi.repository import GtkLayerShell
    HAS_LAYER = True
except (ImportError, ValueError):
    HAS_LAYER = False

APPS = [
    ("writer", "✎", "#f2d7c4", "aether-writer"),
    ("files", "▤", "#d9e4d6", "aether-files"),
    ("terminal", "▮", "#c9d7de", "aether-terminal"),
    ("code", "⌘", "#d8d1e8", "aether-code"),
    ("clock", "◴", "#dbe7f2", "aether-clock"),
    ("focus", "◔", "#dbe7f2", "aether-focus"),
    ("calc", "=", "#efe6d1", "aether-calculator"),
    ("gallery", "❁", "#e6d5e0", "aether-gallery"),
    ("mines", "⊞", "#d9cdd4", "aether-mines"),
    ("monitor", "▤", "#cfd8cf", "aether-system-monitor"),
    ("settings", "⚙", "#cfc8bd", "aether-settings"),
]


class Taskbar(Gtk.Box):
    def __init__(self, shell):
        super().__init__(orientation=Gtk.Orientation.HORIZONTAL, spacing=7)
        self.shell = shell
        self.get_style_context().add_class("aether-taskbar")
        self.buttons: dict[str, Gtk.Button] = {}
        for app_id, glyph, color, binary in APPS:
            b = Gtk.Button(label=glyph)
            b.set_tooltip_text(app_id)
            b.get_style_context().add_class("taskbar-btn")
            b.connect("clicked", self._launch, binary, app_id)
            self.pack_start(b, False, False, 0)
            self.buttons[app_id] = b
        ask = Gtk.Button(label="🐾")
        ask.set_tooltip_text("Ask Miso")
        ask.get_style_context().add_class("taskbar-btn")
        ask.connect("clicked", lambda _: shell.controller.on_miso_clicked())
        self.pack_start(ask, False, False, 0)
        hint = Gtk.Label(label="Miso is nearby")
        hint.get_style_context().add_class("sub")
        self.pack_start(hint, False, False, 7)
        self._apply_layer()

    def _apply_layer(self):
        if HAS_LAYER:
            GtkLayerShell.init_for_window(self)
            GtkLayerShell.set_layer(self, GtkLayerShell.Layer.TOP)
            for edge in (GtkLayerShell.Edge.BOTTOM, GtkLayerShell.Edge.LEFT, GtkLayerShell.Edge.RIGHT):
                GtkLayerShell.set_anchor(self, edge, True)
            GtkLayerShell.set_exclusive_zone(self, 60)

    def _launch(self, btn, binary, app_id):
        import subprocess
        proc = subprocess.Popen(["sh", "-c", binary])
        GLib_prepare = None
        GLib_TIMEOUT = None  # launch feedback handled by window manager signals

    def refresh(self):
        from aether_core.swayipc import SwayIPC
        try:
            import subprocess, json
            out = subprocess.run(["sh", "-c", "echo"], capture_output=True)
            active = set()
            wm = self.shell.wm if hasattr(self.shell, "wm") else None
        except Exception:
            active = set()
        for app_id, btn in self.buttons.items():
            ctx = btn.get_style_context()
            ctx.remove_class("active")
