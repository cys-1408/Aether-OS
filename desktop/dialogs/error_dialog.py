import sys
from pathlib import Path
_p = Path(__file__).resolve()
sys.path.insert(0, str(_p.parents[2]))
sys.path.insert(0, str(_p.parents[3] / 'libraries/libaether-core/python'))
"""Error dialog with the TRUE reason."""
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk


def error_dialog(title: str, reason: str) -> None:
    dlg = Gtk.MessageDialog(modal=True, message_type=Gtk.MessageType.ERROR,
                            buttons=Gtk.ButtonsType.CLOSE, text=title)
    dlg.format_secondary_text(reason)
    dlg.run()
    dlg.destroy()
