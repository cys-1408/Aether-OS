import sys
from pathlib import Path
_p = Path(__file__).resolve()
sys.path.insert(0, str(_p.parents[2]))
sys.path.insert(0, str(_p.parents[3] / 'libraries/libaether-core/python'))
"""One notification row with real close action."""
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk


class NotificationItem(Gtk.Box):
    def __init__(self, data: dict, center):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=2, border_width=6)
        self.get_style_context().add_class("notification-item")
        title = Gtk.Label(label=str(data.get("title", "")), xalign=0)
        title.get_style_context().add_class("fname")
        body = Gtk.Label(label=str(data.get("body", "")), xalign=0)
        body.set_line_wrap(True)
        body.get_style_context().add_class("fpath")
        src = Gtk.Label(label=f"{data.get('source', '')} · {data.get('ts', '')}", xalign=0)
        src.get_style_context().add_class("sub")
        row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        row.pack_start(Gtk.Box(), True, True, 0)
        close = Gtk.Button(label="Dismiss")
        close.get_style_context().add_class("soft")
        nid = data.get("id")
        if nid:
            close.connect("clicked", lambda _, i=nid: self._close(i, center))
        else:
            close.set_sensitive(False)
            close.set_tooltip_text("system entry (cannot dismiss)")
        row.pack_end(close, False, False, 0)
        for wd in (title, body, src, row):
            self.pack_start(wd, False, False, 0)

    def _close(self, nid: str, center):
        from aether_core.ipc import call
        from aether_core import paths
        try:
            call(paths.system_socket("notifications"), "Notify.close", {"id": nid}, timeout=4)
        except Exception:
            pass
        center.refresh()
