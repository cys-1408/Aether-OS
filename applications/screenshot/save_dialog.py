"""Save-as dialog for retaking to a custom path."""
from __future__ import annotations


def save_as(parent, default_path: str) -> str | None:
    import gi
    gi.require_version("Gtk", "3.0")
    from gi.repository import Gtk
    dlg = Gtk.FileChooserDialog(title="Save screenshot", transient_for=parent,
                                action=Gtk.FileChooserAction.SAVE)
    dlg.set_current_name(default_path.rsplit("/", 1)[-1])
    dlg.add_buttons("Cancel", Gtk.ResponseType.CANCEL, "Save", Gtk.ResponseType.OK)
    resp = dlg.run()
    path = dlg.get_filename()
    dlg.destroy()
    return path if resp == Gtk.ResponseType.OK else None
