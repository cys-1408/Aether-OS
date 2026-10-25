"""Central shell state coordinator (thin: delegates to surfaces)."""
from __future__ import annotations

from gi.repository import GLib


class ShellController:
    """Wires cross-surface reactions; surfaces stay single-purpose."""

    def __init__(self, shell):
        self.shell = shell

    def on_miso_clicked(self):
        self.shell.miso_panel.toggle()

    def on_focus_state(self, active: bool, remaining: int | None):
        self.shell.focus_chip.update(active, remaining)
        self.shell.miso.set_state("focused" if active else "idle")
        self.shell.top_bar.set_status("FOCUS MODE" if active else "All calm")

    def on_window_state(self):
        self.shell.taskbar.refresh()
