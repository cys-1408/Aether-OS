"""Keyboard navigation (sticky/slow keys) via GSettings."""
from __future__ import annotations


def configure(sticky: bool = False, slow: bool = False) -> dict:
    try:
        from gi.repository import Gio
        s = Gio.Settings.new("org.gnome.desktop.a11y.keyboard")
        s.set_boolean("stickykeys-enable", sticky)
        s.set_boolean("slowkeys-enable", slow)
        return {"sticky": sticky, "slow": slow}
    except Exception as e:  # noqa: BLE001
        return {"error": str(e)}
