"""Sidebar + stacked pages (all real)."""
from __future__ import annotations

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

PAGES = [
    ("appearance", "Appearance", "appearance_page"),
    ("display", "Display", "display_page"),
    ("audio", "Audio", "audio_page"),
    ("network", "Network", "network_page"),
    ("power", "Power", "power_page"),
    ("users", "Users", "user_accounts_page"),
    ("privacy", "Privacy", "privacy_page"),
    ("permissions", "Permissions", "permissions_page"),
    ("accessibility", "Accessibility", "accessibility_page"),
    ("ai", "AI Runtime", "ai_runtime_page"),
    ("intentfs", "IntentFS", "intentfs_page"),
    ("updates", "Updates", "updates_page"),
    ("backup", "Backup & Recovery", "backup_recovery_page"),
]


class SettingsShell(Gtk.Box):
    def __init__(self, app):
        super().__init__(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        self.app = app
        side = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2, border_width=10)
        self.stack = Gtk.Stack()
        for key, label, module in PAGES:
            b = Gtk.Button(label=label)
            b.get_style_context().add_class("flat")
            b.connect("clicked", self._show, key)
            side.pack_start(b, False, False, 0)
            try:
                mod = __import__(module)
                self.stack.add_named(mod.build_page(app), key)
            except Exception as e:  # surface real page errors honestly
                err = Gtk.Label(label=f"{label} page failed to load: {e}")
                err.set_line_wrap(True)
                self.stack.add_named(err, key)
        side.set_size_request(150, -1)
        self.pack_start(side, False, False, 0)
        self.pack_start(Gtk.Separator(orientation=Gtk.Orientation.VERTICAL), False, False, 0)
        self.pack_start(self.stack, True, True, 0)

    def _show(self, _btn, key):
        self.stack.set_visible_child_name(key)
