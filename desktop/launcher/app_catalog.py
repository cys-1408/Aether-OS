"""Catalog: real desktop entries + registered system actions."""
from __future__ import annotations

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gio


def build_catalog() -> list[dict]:
    items = []
    seen = set()
    for app in Gio.AppInfo.get_all():
        if app.should_show() and app.get_id() not in seen:
            seen.add(app.get_id())
            items.append({"kind": "app", "name": app.get_display_name() or app.get_id(),
                          "exec": app.get_commandline() or app.get_executable()})
    # Registered system actions (typed; validated against service methods)
    items += [
        {"kind": "action", "name": "Open Settings", "service": "shell",
         "method": "Shell.open_app", "params": {"app": "settings"}},
        {"kind": "action", "name": "Start a focus session", "service": "shell",
         "method": "Shell.start_focus", "params": {"minutes": 25}},
        {"kind": "action", "name": "Organize windows", "service": "shell",
         "method": "Shell.tile_windows", "params": {}},
        {"kind": "action", "name": "Check for updates", "service": "updates",
         "method": "Updates.check", "params": {}},
        {"kind": "action", "name": "Open System Monitor", "service": "shell",
         "method": "Shell.open_app", "params": {"app": "monitor"}},
    ]
    return items
