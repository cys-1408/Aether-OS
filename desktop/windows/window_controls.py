"""Close/min/max control implementations (real WM ops)."""
from __future__ import annotations


def make_controls(win: Gtk.Window, wm=None, wid: int | None = None):
    def close(_btn):
        win.close()

    def minimize(_btn):
        if wm and wid:
            wm.minimize_window(wid)
        else:
            win.iconify()

    def maximize(_btn):
        if wm and wid:
            wm.maximize_window(wid)
        else:
            win.is_maximized() and win.unmaximize() or win.maximize()
    return close, minimize, maximize
