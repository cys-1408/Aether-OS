"""Aether Settings — every page wired to real services/GSettings."""
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

from settings_shell import SettingsShell


class SettingsApp(AetherApp):
    app_id = "org.aether.Apps.Settings"
    title = "Settings"

    def build_window(self):
        win = super().build_window()
        win.set_default_size(560, 460)
        win.add(SettingsShell(self))
        return win


if __name__ == "__main__":
    sys.exit(SettingsApp().run(sys.argv))
