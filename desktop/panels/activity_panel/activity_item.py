import sys
from pathlib import Path
_p = Path(__file__).resolve()
sys.path.insert(0, str(_p.parents[2]))
sys.path.insert(0, str(_p.parents[3] / 'libraries/libaether-core/python'))
"""Activity row model for the panel list view."""
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk


class ActivityItem(Gtk.Box):
    def __init__(self, entry: dict):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        line = Gtk.Label(label=f"{entry.get('timestamp', '')} · {entry.get('result', '')}", xalign=0)
        line.get_style_context().add_class("sub")
        self.pack_start(line, False, False, 0)
