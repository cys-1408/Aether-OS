"""Network choice screen: online install (Network.status) or fully offline."""

from __future__ import annotations

from ..._bootstrap import call_system_socket
from ..installer_error import InstallerError
from .base_screen import ScreenBase


def network_status() -> dict:
    """Query the network service; fall back to nmcli; else report unknown."""
    result = call_system_socket("network", "Network.status", {}, timeout=5.0)
    if result is not None:
        return result
    try:
        import subprocess

        proc = subprocess.run(
            ["nmcli", "-t", "-f", "STATE,CONNECTIVITY", "general", "status"],
            capture_output=True, timeout=10,
        )
        if proc.returncode == 0:
            fields = proc.stdout.decode().strip().split("\n")[0].split(":")
            state = fields[0] if fields else "unknown"
            connectivity = fields[1] if len(fields) > 1 else "unknown"
            return {
                "state": state,
                "connectivity": connectivity,
                "online": connectivity in ("full", "limited", "portal"),
            }
    except (OSError, subprocess.TimeoutExpired):
        pass
    return {"state": "unavailable", "online": False, "reason": "network service not reachable"}


class NetworkChoiceScreen(ScreenBase):
    title = "Network"
    subtitle = ("Online installation fetches the newest packages. Offline "
                "installation uses only what ships on the ISO; AetherOS is "
                "fully functional offline.")

    def _build_gtk(self):
        from gi.repository import Gtk

        box = self.gtk_box(spacing=12)
        box.pack_start(self.gtk_heading(), False, False, 0)

        status = network_status()
        self.controller.apply("network_status", status)
        status_label = Gtk.Label(xalign=0.0)
        state = status.get("state", "unknown")
        online = bool(status.get("online"))
        status_label.set_markup(
            f"Network service: <b>{state}</b> — "
            + ("<span foreground='#1a7f37'>online</span>" if online
               else "no connectivity detected")
        )
        box.pack_start(status_label, False, False, 0)

        radio_online = Gtk.RadioButton.with_label_from_widget(None, "Online install")
        radio_offline = Gtk.RadioButton.with_label_from_widget(
            radio_online, "Offline install (media only)")
        mode = self.controller.get("network_mode")
        (radio_offline if mode == "offline" else radio_online).set_active(True)
        radio_online.connect("toggled", self._on_online)
        radio_offline.connect("toggled", self._on_offline)
        box.pack_start(radio_online, False, False, 0)
        box.pack_start(radio_offline, False, False, 0)
        self._radio_online = radio_online
        return box

    def _on_online(self, radio):
        if radio.get_active():
            self.controller.apply("network_mode", "online")

    def _on_offline(self, radio):
        if radio.get_active():
            self.controller.apply("network_mode", "offline")

    def run_cli(self) -> None:
        self.cli_header()
        status = network_status()
        self.controller.apply("network_status", status)
        state = status.get("state", "unknown")
        online = bool(status.get("online"))
        self.cli_print(f"Network service: {state} "
                       f"({'online' if online else 'no connectivity detected'})")
        mode = self.cli_choose(
            "Installation mode",
            ["online", "offline"],
            default=None if online else "offline",
        )
        self.controller.apply("network_mode", mode)
        if mode == "online" and not online:
            self.cli_print(
                "Warning: no connectivity detected; package downloads may fail."
            )
