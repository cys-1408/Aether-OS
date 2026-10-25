"""Gtk.Application owning every shell surface + the Shell.* IPC server."""
from __future__ import annotations

import threading

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GLib

from aether_core import paths
from aether_core.ipc import JsonRpcServer
from aether_core.logging_setup import configure_logging

from window_manager.window_capabilities import WindowCapabilities
from panels.top_bar.top_bar import TopBar
from panels.taskbar.taskbar import Taskbar
from panels.activity_panel.activity_panel import ActivityPanel
from panels.notification_center.notification_center import NotificationCenter
from panels.focus_chip.focus_chip import FocusChip
from miso_view.miso_companion_view import MisoCompanionView
from miso_view.miso_panel import MisoPanel
from focus_mode.focus_controller import FocusController
from notifications.toast_manager import ToastManager
from dialogs.permission_dialog import PermissionDialog
from theme.widget_style import load_css

log = configure_logging("shell")


class ShellApplication(Gtk.Application):
    def __init__(self):
        super().__init__(application_id="org.aether.Shell")

    def do_startup(self):
        Gtk.Application.do_startup(self)
        load_css()

    def do_activate(self):
        self.win = Gtk.Window(application=self, title="Aether Desktop")
        self.win.set_decorated(False)
        self.win.fullscreen()
        self.win.set_accept_focus(False)
        self.win.set_keep_below(True)

        self.wm = WindowCapabilities()
        self.focus = FocusController(self.wm)
        self.toasts = ToastManager(self.win)

        overlay = Gtk.Overlay()
        self.win.add(overlay)

        self.top_bar = TopBar(self)
        self.taskbar = Taskbar(self)
        self.activity = ActivityPanel(self)
        self.notif_center = NotificationCenter(self)
        self.focus_chip = FocusChip(self)
        self.miso = MisoCompanionView(self)
        self.miso_panel = MisoPanel(self)

        for surface in (self.top_bar, self.taskbar, self.activity,
                        self.notif_center, self.focus_chip, self.miso):
            try:
                overlay.add_overlay(surface)
            except Exception:
                surface.set_parent(self.win)
        self.win.show_all()

        self._start_ipc()

    # ------------------------------------------------------------------ IPC
    def _start_ipc(self):
        paths.ensure_user_dirs()
        caps = WindowCapabilities()

        def confirm(params: dict) -> dict:
            """Broker-only confirmation surface (peer uid checked by broker)."""
            resp = {"approved": False}

            def ask():
                dlg = PermissionDialog(self.win, params)
                resp["approved"] = dlg.run_confirm()
                return False

            GLib.idle_add(ask)
            return resp

        methods = caps.methods()
        methods.update({
            "Shell.toast": lambda p: self.toasts.show(str(p.get("title", "")), str(p.get("body", ""))) or {"shown": True},
            "Shell.start_focus": lambda p: self.focus.start(int(p.get("minutes", 25)), p.get("target_app")) or {"started": True},
            "Shell.pause_focus": lambda p: self.focus.pause() or {"paused": True},
            "Shell.end_focus": lambda p: self.focus.end() or {"ended": True},
            "Broker.confirm": confirm,
        })
        from aether_core.version import API_VERSIONS
        methods["X.info"] = lambda p: {"service": "shell", "api_version": API_VERSIONS["shell"]}
        self._server = JsonRpcServer(paths.user_socket("shell"), methods)
        threading.Thread(target=self._server.serve_forever, daemon=True).start()
        log.info("Shell IPC ready")
