import sys
from pathlib import Path
_p = Path(__file__).resolve()
sys.path.insert(0, str(_p.parents[2]))
sys.path.insert(0, str(_p.parents[3] / 'libraries/libaether-core/python'))
"""ATK roles/names for every custom widget (screen-reader contract)."""
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk


def set_role(widget: Gtk.Widget, role, name: str, description: str = "") -> None:
    widget.get_accessible().set_role(role)
    widget.get_accessible().set_name(name)
    if description:
        widget.get_accessible().set_description(description)


def label_for_button(btn: Gtk.Button, name: str) -> None:
    set_role(btn, Atk.Role.PUSH_BUTTON if hasattr(Atk, "Role") else None, name)


def announce(widget: Gtk.Widget, text: str) -> None:
    acc = widget.get_accessible()
    try:
        acc.notify_state_change(1, text)
    except Exception:
        pass
