"""Desktop entry enumeration + validation (no invented apps)."""
from __future__ import annotations

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gio


def installed_apps() -> list[dict]:
    out = []
    for app in Gio.AppInfo.get_all():
        if app.should_show():
            out.append({
                "id": app.get_id(),
                "name": app.get_display_name(),
                "description": app.get_description() or "",
                "executable": app.get_executable(),
                "commandline": app.get_commandline(),
            })
    return out
