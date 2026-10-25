import sys
from pathlib import Path
_p = Path(__file__).resolve()
sys.path.insert(0, str(_p.parents[2]))
sys.path.insert(0, str(_p.parents[3] / 'libraries/libaether-core/python'))
"""Native file chooser wrapper."""
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk


def choose_file(parent=None, title: str = "Open file", save: bool = False) -> str | None:
    action = Gtk.FileChooserAction.SAVE if save else Gtk.FileChooserAction.OPEN
    dlg = Gtk.FileChooserDialog(title=title, transient_for=parent, action=action)
    dlg.add_buttons("Cancel", Gtk.ResponseType.CANCEL,
                    "Save" if save else "Open", Gtk.ResponseType.OK)
    resp = dlg.run()
    path = dlg.get_filename()
    dlg.destroy()
    return path if resp == Gtk.ResponseType.OK else None


def choose_folder(parent=None, title: str = "Choose folder") -> str | None:
    dlg = Gtk.FileChooserDialog(title=title, transient_for=parent,
                                action=Gtk.FileChooserAction.SELECT_FOLDER)
    dlg.add_buttons("Cancel", Gtk.ResponseType.CANCEL, "Select", Gtk.ResponseType.OK)
    resp = dlg.run()
    path = dlg.get_filename()
    dlg.destroy()
    return path if resp == Gtk.ResponseType.OK else None
