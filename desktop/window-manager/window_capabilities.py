"""Shell.* capability surface: the broker's route to the desktop."""
from __future__ import annotations

import shlex

from window_manager import WindowManager
from tiling_layout import tile_windows, arrange_side_by_side
from virtual_desktops import workspaces


class WindowCapabilities:
    def __init__(self):
        self.wm = WindowManager()
        self._app_commands = {
            "files": ["aether-files"], "writer": ["aether-writer"],
            "terminal": ["aether-terminal"], "code": ["aether-code"],
            "clock": ["aether-clock"], "focus": ["aether-focus"],
            "calc": ["aether-calculator"], "calculator": ["aether-calculator"],
            "gallery": ["aether-gallery"], "mines": ["aether-mines"],
            "monitor": ["aether-system-monitor"], "settings": ["aether-settings"],
            "software-center": ["aether-software-center"],
            "screenshot": ["aether-screenshot"], "archive-manager": ["aether-archive-manager"],
            "backup-center": ["aether-backup-center"], "recovery-center": ["aether-recovery-center"],
        }

    def methods(self) -> dict:
        return {
            "Shell.list_apps": self.list_apps,
            "Shell.open_app": self.open_app,
            "Shell.close_app": self.close_app,
            "Shell.focus_app": self.focus_app,
            "Shell.list_windows": lambda p: {"windows": self.wm.windows()},
            "Shell.arrange_windows": lambda p: arrange_side_by_side(self.wm),
            "Shell.tile_windows": lambda p: tile_windows(self.wm),
            "Shell.minimize_window": lambda p: self.wm.minimize_window(int(p.get("window_id", 0))),
            "Shell.restore_window": lambda p: self.wm.restore_window(int(p.get("window_id", 0))),
            "Shell.create_workspace": lambda p: self.wm.create_workspace(str(p.get("name", "ws"))),
            "Shell.list_workspaces": lambda p: {"workspaces": workspaces()},
        }

    # ------------------------------------------------------------------ impls
    def list_apps(self, params: dict) -> dict:
        import gi
        gi.require_version("Gtk", "3.0")
        from gi.repository import Gio
        apps = []
        for app in Gio.AppInfo.get_all():
            if app.should_show():
                apps.append({"id": app.get_id(), "name": app.get_display_name(),
                             "description": app.get_description() or ""})
        return {"apps": apps}

    def open_app(self, params: dict) -> dict:
        app = str(params.get("app", "")).strip().lower()
        if app in self._app_commands:
            return self.wm.launch_app(self._app_commands[app])
        import gi
        gi.require_version("Gtk", "3.0")
        from gi.repository import Gio
        for info in Gio.AppInfo.get_all():
            if app in (info.get_id() or "").lower() or app == (info.get_display_name() or "").lower():
                return {"launched": info.launch([], Gio.AppLaunchContext()) is not False}
        return {"error": f"no installed application matches {app!r}"}

    def close_app(self, params: dict) -> dict:
        app = str(params.get("app", "")).lower()
        closed = []
        for win in self.wm.windows():
            if app and app in (win.get("app_id") or "").lower():
                closed.append(self.wm.close_window(win["id"]))
        return {"closed": closed} if closed else {"error": f"no open window for {app!r}"}

    def focus_app(self, params: dict) -> dict:
        app = str(params.get("app", "")).lower()
        for win in self.wm.windows():
            if app in (win.get("app_id") or "").lower():
                return self.wm.focus_window(win["id"])
        return {"error": f"no open window for {app!r}"}
