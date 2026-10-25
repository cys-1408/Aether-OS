import sys
from pathlib import Path
_p = Path(__file__).resolve()
sys.path.insert(0, str(_p.parents[2]))
sys.path.insert(0, str(_p.parents[3] / 'libraries/libaether-core/python'))
"""Completion surface: what actually happened (real session data)."""
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk


class FocusCompletionView(Gtk.Box):
    def __init__(self, minutes: int, completed: bool):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        title = Gtk.Label(label="Session completed!" if completed else "Session ended")
        title.get_style_context().add_class("h1")
        detail = Gtk.Label(label=f"{minutes} minutes of focus."
                           + ("" if completed else " You ended it early — still counts."))
        detail.get_style_context().add_class("sub")
        self.pack_start(title, False, False, 0)
        self.pack_start(detail, False, False, 0)
