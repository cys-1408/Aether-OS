import sys
from pathlib import Path
_p = Path(__file__).resolve()
sys.path.insert(0, str(_p.parents[2]))
sys.path.insert(0, str(_p.parents[3] / 'libraries/libaether-core/python'))
"""Window context menu (real operations)."""
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk


def popup(win, wm, wid: int, event):
    menu = Gtk.Menu()
    for label, cb in (("Minimize", lambda _: wm.minimize_window(wid)),
                      ("Maximize", lambda _: wm.maximize_window(wid)),
                      ("Tile all", lambda _: wm.adapter.run("smart tiled") or None),
                      ("Close", lambda _: wm.close_window(wid))):
        item = Gtk.MenuItem(label=label)
        item.connect("activate", cb)
        menu.append(item)
    menu.show_all()
    menu.popup_at_pointer(event)
