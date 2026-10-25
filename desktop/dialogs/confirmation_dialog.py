import sys
from pathlib import Path
_p = Path(__file__).resolve()
sys.path.insert(0, str(_p.parents[2]))
sys.path.insert(0, str(_p.parents[3] / 'libraries/libaether-core/python'))
"""Generic confirmation dialog (real user intent gate)."""
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk


def confirm_dialog(title: str, message: str) -> bool:
    dlg = Gtk.MessageDialog(transient_for=None, modal=True,
                            message_type=Gtk.MessageType.QUESTION,
                            buttons=Gtk.ButtonsType.OK_CANCEL, text=title)
    dlg.format_secondary_text(message)
    resp = dlg.run()
    dlg.destroy()
    return resp == Gtk.ResponseType.OK
