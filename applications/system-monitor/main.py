"""Aether System Monitor — real process table, CPU/mem graphs, services."""
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
from gi.repository import Gtk, GLib

from process_table import ProcessTable
from cpu_graph import CpuGraph
from memory_graph import MemoryGraph
from service_status_view import ServiceStatusView


class MonitorWindow(Gtk.Box):
    def __init__(self, app):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=8, border_width=12)
        self.app = app
        top = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        top.pack_start(CpuGraph(), True, True, 0)
        top.pack_start(MemoryGraph(), True, True, 0)
        self.pack_start(top, False, False, 0)

        self.pack_start(Gtk.Label(label="Processes", xalign=0).get_style_context().add_class("eyebrow") or Gtk.Label(label=""), False, False, 0)
        self.proc = ProcessTable()
        scroll = Gtk.ScrolledWindow()
        scroll.set_vexpand(True)
        scroll.add(self.proc.tree)
        self.pack_start(scroll, True, True, 0)

        actions = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        kill = Gtk.Button(label="End process")
        kill.get_style_context().add_class("soft")
        kill.connect("clicked", self._kill)
        actions.pack_start(kill, False, False, 0)
        self.pack_start(actions, False, False, 0)

        self.services = ServiceStatusView(app)
        self.pack_start(self.services, False, False, 0)
        GLib.timeout_add_seconds(2, self._refresh)

    def _refresh(self):
        self.proc.refresh()
        self.services.refresh()
        return True

    def _kill(self, _btn):
        from desktop.dialogs.destructive_action_dialog import DestructiveActionDialog
        pid, name = self.proc.selected()
        if not pid:
            return
        dlg = DestructiveActionDialog(self.get_toplevel(), "End process", f"{name} (pid {pid})")
        if dlg.run_confirm():
            self.proc.kill(pid)


class MonitorApp(AetherApp):
    app_id = "org.aether.Apps.SystemMonitor"
    title = "Monitor"

    def build_window(self):
        win = super().build_window()
        win.set_default_size(560, 480)
        win.add(MonitorWindow(self))
        return win


if __name__ == "__main__":
    sys.exit(MonitorApp().run(sys.argv))
