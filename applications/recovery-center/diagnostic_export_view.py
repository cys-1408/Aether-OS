"""Redacted diagnostic export with explicit consent checkbox."""
from __future__ import annotations

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk


def export_bundle(app) -> str:
    dlg = Gtk.MessageDialog(text="Export a redacted diagnostic bundle?",
                            secondary_text="Contains service states, kernel version, hardware summary and recent error logs — all secret-redacted.",
                            buttons=Gtk.ButtonsType.OK_CANCEL)
    if dlg.run() != Gtk.ResponseType.OK:
        dlg.destroy()
        return "export cancelled"
    dlg.destroy()
    result = app.services.call("logs", "Logs.bundle",
                               {"consent": True,
                                "scope": ["kernel_version", "unit_states", "hardware_summary",
                                          "failed_units_journal_200_lines"]}, timeout=120)
    return str(result)
