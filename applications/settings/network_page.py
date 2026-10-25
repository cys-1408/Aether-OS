"""Network page: wifi list/connect via Network.* services."""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[2]
for p in (REPO_ROOT / "libraries/libaether-core/python", REPO_ROOT / "applications/app-framework"):
    sys.path.insert(0, str(p))

from application_context import AetherApp  # noqa: E402

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GLib


def build_page(app) -> Gtk.Box:
    box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8, border_width=16)
    status = app.services.call("network", "Network.status", {})
    general = (status or {}).get("general", {})
    box.pack_start(Gtk.Label(label=f"Networking: {general.get('networking', 'unknown')} · "
                                     f"connectivity: {general.get('connectivity', 'unknown')}", xalign=0), False, False, 0)
    scan_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
    scan_btn = Gtk.Button(label="Scan Wi-Fi")
    scan_btn.get_style_context().add_class("btn")
    scan_row.pack_start(scan_btn, False, False, 0)
    box.pack_start(scan_row, False, False, 0)
    listbox = Gtk.ListBox()
    scroll = Gtk.ScrolledWindow()
    scroll.set_vexpand(True)
    scroll.add(listbox)
    box.pack_start(scroll, True, True, 0)

    def do_scan(_btn):
        import threading
        def work():
            data = app.services.call("network", "Network.wifi_scan", {}, timeout=30)
            nets = (data or {}).get("networks", [])
            reason = (data or {}).get("reason") if data and not nets else None
            GLib.idle_add(_fill, nets, reason)
        threading.Thread(target=work, daemon=True).start()

    def _fill(nets, reason):
        for c in listbox.get_children():
            listbox.remove(c)
        if reason:
            listbox.add(Gtk.Label(label=f"scan unavailable: {reason}"))
        for net in nets:
            row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
            row.pack_start(Gtk.Label(label=f"{net['ssid']} ({net['signal']}%) {'●' if net.get('connected') else ''}", xalign=0), True, True, 0)
            btn = Gtk.Button(label="Connect")
            btn.get_style_context().add_class("soft")
            btn.connect("clicked", _connect, net["ssid"])
            row.pack_end(btn, False, False, 0)
            listbox.add(row)
        listbox.show_all()

    def _connect(_btn, ssid):
        dlg = Gtk.Dialog(title=f"Connect to {ssid}", transient_for=None)
        dlg.add_button("Cancel", Gtk.ResponseType.CANCEL)
        dlg.add_button("Connect", Gtk.ResponseType.OK)
        entry = Gtk.Entry()
        entry.set_visibility(False)
        entry.set_placeholder_text("password (leave empty for open networks)")
        dlg.get_content_area().pack_start(entry, False, False, 8)
        dlg.show_all()
        if dlg.run() == Gtk.ResponseType.OK:
            app.services.call("network", "Network.wifi_connect",
                              {"ssid": ssid, "password": entry.get_text()}, timeout=60)
        dlg.destroy()

    scan_btn.connect("clicked", do_scan)
    return box
