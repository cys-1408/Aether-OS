import sys
from pathlib import Path
_p = Path(__file__).resolve()
sys.path.insert(0, str(_p.parents[2]))
sys.path.insert(0, str(_p.parents[3] / 'libraries/libaether-core/python'))
"""Permission dialog: shows the EXACT capability, targets and risk."""
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

RISK_LABELS = {"read_only": "read-only", "low_reversible": "reversible",
               "write": "changes things", "destructive": "destructive"}


class PermissionDialog(Gtk.MessageDialog):
    def __init__(self, parent, params: dict):
        cap = params.get("capability_id", "action")
        risk = params.get("risk_class", "write")
        targets = params.get("targets") or params.get("params", {})
        super().__init__(transient_for=parent, modal=True,
                         message_type=Gtk.MessageType.QUESTION,
                         buttons=Gtk.ButtonsType.OK_CANCEL,
                         text=f"Allow Miso to {cap}?")
        lines = [f"Risk: {RISK_LABELS.get(risk, risk)}.",
                 f"Targets: {targets if targets else 'see details'}"]
        self.format_secondary_text("\n".join(str(l) for l in lines))

    def run_confirm(self) -> bool:
        resp = self.run()
        self.destroy()
        return resp == Gtk.ResponseType.OK
