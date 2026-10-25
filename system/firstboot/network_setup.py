"""Network page: state report + optional connect (offline install supported)."""
from __future__ import annotations

import subprocess


def network_state() -> dict:
    try:
        out = subprocess.run(["nmcli", "-t", "-f", "STATE,CONNECTIVITY", "general", "status"],
                             capture_output=True, text=True, timeout=10)
        if out.returncode == 0:
            state, conn = out.stdout.strip().split(":", 1)
            return {"networking": state, "connectivity": conn}
        return {"networking": "unknown", "error": out.stderr.strip()}
    except FileNotFoundError:
        return {"networking": "unavailable", "error": "nmcli not installed"}


def enable_networking(enable: bool) -> dict:
    try:
        subprocess.run(["nmcli", "networking", "on" if enable else "off"], check=True, timeout=15)
        return {"ok": True, "enabled": enable}
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError) as e:
        return {"ok": False, "error": str(e)}


def run_cli_prompt() -> dict:
    print("Network:", network_state())
    choice = input("Enable networking? [Y/n]: ").strip().lower() != "n"
    enable_networking(choice)
    return {"networking_enabled": choice}


def gtk_widget(commit):
    import gi
    gi.require_version("Gtk", "3.0")
    from gi.repository import Gtk
    box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
    state = Gtk.Label(label=str(network_state()))
    enable = Gtk.CheckButton(label="Enable networking (optional — install works offline)")
    enable.set_active(True)
    btn = Gtk.Button(label="Continue")

    def _next(_):
        enable_networking(enable.get_active())
        commit("network", {"networking_enabled": enable.get_active()})
    btn.connect("clicked", _next)
    box.pack_start(state, False, False, 0)
    box.pack_start(enable, False, False, 0)
    box.pack_start(btn, False, False, 0)
    return box
