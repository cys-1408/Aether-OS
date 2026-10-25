"""Active window indicator driven by the sway tree."""
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk


class ActiveAppIndicator:
    def __init__(self, taskbar):
        self.taskbar = taskbar

    def update(self, windows: list[dict]):
        focused = next((w for w in windows if w.get("focused")), None)
        for app_id, btn in self.taskbar.buttons.items():
            ctx = btn.get_style_context()
            active = bool(focused and app_id in (focused.get("app_id") or ""))
            if active:
                ctx.add_class("active")
            else:
                ctx.remove_class("active")
