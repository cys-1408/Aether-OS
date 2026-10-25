"""Resource usage widget. (GTK3, guarded imports; data via Runtime IPC)."""
from __future__ import annotations

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

from aether_core.ipc import call
from aether_core.errors import IpcError
from aether_core import paths


def build_widget() -> Gtk.Widget:
    box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
    label = Gtk.Label(label="AI runtime: checking...", xalign=0)
    box.pack_start(label, False, False, 0)
    try:
        status = call(paths.system_socket("runtime"), "Runtime.status", {}, timeout=5)
        state = status.get("state", "unknown") if status else "unreachable"
        label.set_text("AI runtime: " + str(state))
    except IpcError as e:
        label.set_text("AI runtime: unavailable (" + e.message + ")")
    return box
