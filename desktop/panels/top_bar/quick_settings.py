"""Quick settings popover: volume, wifi, mic mute, power — all real calls."""
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

from system_status_widget import SystemStatusWidget


class QuickSettings(Gtk.Popover):
    def __init__(self, parent_btn: Gtk.Button):
        super().__init__()
        self.set_relative_to(parent_btn)
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10, border_width=14)
        box.add(SystemStatusWidget())

        vol_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        vol_row.add(Gtk.Label(label="Volume"))
        scale = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 0, 100, 5)
        scale.set_value(50)
        scale.set_size_request(160, -1)

        def vol_changed(_):
            self._call("audio", "Audio.set_volume", {"target": "sink", "percent": int(scale.get_value())})
        scale.connect("value-changed", vol_changed)
        vol_row.pack_start(scale, True, True, 0)
        box.add(vol_row)

        self.wifi_btn = Gtk.CheckButton(label="Wi-Fi")
        self.wifi_btn.connect("toggled", self._wifi_toggled)
        box.add(self.wifi_btn)

        self.mic_btn = Gtk.CheckButton(label="Microphone live")
        self.mic_btn.connect("toggled", self._mic_toggled)
        box.add(self.mic_btn)

        power_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        for label, verb in (("Suspend", "suspend"), ("Reboot", "reboot"), ("Power off", "poweroff")):
            b = Gtk.Button(label=label)
            b.get_style_context().add_class("btn")
            b.connect("clicked", lambda _b, v=verb: self._power(v))
            power_row.pack_start(b, False, False, 0)
        box.add(power_row)
        box.show_all()
        self.add(box)

    @staticmethod
    def _call(service: str, method: str, params: dict) -> dict | None:
        from aether_core.ipc import call
        from aether_core.errors import IpcError
        from aether_core import paths
        try:
            return call(paths.resolve_socket(service), method, params, timeout=5)
        except IpcError as e:
            return {"error": e.message}

    def _wifi_toggled(self, btn):
        self._call("network", "Network.enable" if btn.get_active() else "Network.disable", {})

    def _mic_toggled(self, btn):
        self._call("audio", "Audio.set_mic_muted", {"muted": not btn.get_active()})

    def _power(self, verb: str):
        import subprocess
        from dialogs.confirmation_dialog import confirm_dialog
        if confirm_dialog("Power", f"Really {verb} now?"):
            subprocess.Popen(["systemctl", verb])
