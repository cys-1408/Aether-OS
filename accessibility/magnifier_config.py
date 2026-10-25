"""Magnifier config (GNOME magnifier-compatible keys)."""
from __future__ import annotations


def configure(enabled: bool, factor: float = 2.0) -> dict:
    try:
        from gi.repository import Gio
        s = Gio.Settings.new("org.gnome.desktop.a11y.applications")
        s.set_boolean("screen-magnifier-enabled", enabled)
        s.set_double("mag-factor", factor)
        return {"magnifier": enabled, "factor": factor}
    except Exception as e:  # noqa: BLE001
        return {"error": str(e)}
