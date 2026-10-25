import sys
from pathlib import Path
_p = Path(__file__).resolve()
sys.path.insert(0, str(_p.parents[2]))
sys.path.insert(0, str(_p.parents[3] / 'libraries/libaether-core/python'))
"""Destructive confirmation: requires typing the exact target name."""
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk


class DestructiveActionDialog(Gtk.Dialog):
    def __init__(self, parent, action: str, target: str):
        super().__init__(title="Destructive action", transient_for=parent, modal=True)
        self.target = target
        box = self.get_content_area()
        box.set_spacing(10)
        box.set_border_width(14)
        box.add(Gtk.Label(label=f"⚠ {action}\nThis will affect: {target}\n"
                                 f"Type the target name to confirm:"))
        self.entry = Gtk.Entry()
        box.add(self.entry)
        self.add_button("Cancel", Gtk.ResponseType.CANCEL)
        self.add_button("Confirm", Gtk.ResponseType.OK)
        self.show_all()

    def run_confirm(self) -> bool:
        resp = self.run()
        typed = self.entry.get_text().strip()
        self.destroy()
        return resp == Gtk.ResponseType.OK and typed == self.target
