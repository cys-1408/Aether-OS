"""Restore wizard: preview → policy → real restore."""
from __future__ import annotations

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from pathlib import Path


def run_restore_wizard(app, parent):
    from desktop.dialogs.file_picker_adapter import choose_file
    backup = choose_file(parent, "Choose backup file")
    if not backup:
        return
    preview = app.services.call("backup", "Backup.restore_preview", {"file": backup})
    if not preview or not preview.get("ok"):
        msg = (preview or {}).get("reason", "preview unavailable")
        Gtk.MessageDialog(text="Restore preview failed", secondary_text=msg,
                          buttons=Gtk.ButtonsType.CLOSE).run()
        return
    dlg = Gtk.Dialog(title="Restore preview", transient_for=parent)
    dlg.add_button("Cancel", Gtk.ResponseType.CANCEL)
    dlg.add_button("Restore (rename conflicts)", Gtk.ResponseType.OK)
    text = (f"restorable: {preview.get('restorable', 0)}\n"
            f"conflicts: {len(preview.get('conflicts', []))}")
    dlg.get_content_area().pack_start(Gtk.Label(label=text), False, False, 10)
    dlg.show_all()
    if dlg.run() == Gtk.ResponseType.OK:
        result = app.services.call("backup", "Backup.restore",
                                   {"file": backup, "conflict_policy": "rename"}, timeout=3600)
        report = Gtk.MessageDialog(text="Restore result", secondary_text=str(result)[:600],
                                   buttons=Gtk.ButtonsType.CLOSE)
        report.run(); report.destroy()
    dlg.destroy()
