"""Reduced motion: GSettings-driven; disables Miso/panel animation."""
from __future__ import annotations

from shell_settings import settings


def enabled() -> bool:
    return settings().get_boolean("reduced-motion")


def set_enabled(on: bool, shell=None) -> None:
    settings().set_boolean("reduced-motion", on)
    if shell is not None and hasattr(shell, "miso"):
        if on:
            shell.miso.enable_reduced_motion()
        else:
            shell.miso.reduced_motion = False


def prefers_reduced_motion_system() -> bool:
    # GTK has no direct port of prefers-reduced-motion; read the XDG portal when present
    try:
        from gi.repository import Gio
        s = Gio.Settings.new("org.gnome.desktop.interface")
        return s.get_boolean("gtk-enable-animations") is False
    except Exception:
        return False
