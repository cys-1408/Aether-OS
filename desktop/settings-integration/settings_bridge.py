"""Bridge between the Settings app and shell GSettings (live both ways)."""
from __future__ import annotations

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gio

from shell_settings import settings, SCHEMA_ID


def watch(key: str, callback) -> None:
    settings().connect(f"changed::{key}", lambda s, k: callback(s.get_value(k)))


def export_state() -> dict:
    s = settings()
    out = {}
    for key in ("distraction-protection", "auto-organize", "reduced-motion",
                "text-only-mode", "focus-minutes", "miso-enabled",
                "high-contrast", "font-scale"):
        schema_type = Gio.SettingsSchemaSource.get_default().lookup(SCHEMA_ID, False)
        v = s.get_value(key)
        out[key] = v.unpack() if hasattr(v, "unpack") else v
    return out
