"""Encryption status page: read-only real LUKS report."""
from __future__ import annotations

import subprocess


def status() -> dict:
    try:
        out = subprocess.run(["lsblk", "-J", "-o", "NAME,TYPE,FSTYPE"],
                             capture_output=True, text=True, timeout=10)
        import json
        data = json.loads(out.stdout)
        encrypted = []
        def walk(nodes):
            for n in nodes:
                if n.get("fstype") == "crypto_LUKS":
                    encrypted.append(n.get("name"))
                walk(n.get("children") or [])
        walk(data.get("blockdevices", []))
        return {"encrypted_devices": encrypted, "encrypted": bool(encrypted)}
    except (FileNotFoundError, subprocess.TimeoutExpired, json.JSONDecodeError) as e:
        return {"encrypted": None, "error": str(e)}


def run_cli_prompt() -> dict:
    s = status()
    print("Disk encryption:", "enabled" if s.get("encrypted") else "not detected")
    return {"disk_encryption": bool(s.get("encrypted"))}


def gtk_widget(commit):
    import gi
    gi.require_version("Gtk", "3.0")
    from gi.repository import Gtk
    box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
    s = status()
    box.pack_start(Gtk.Label(label="Disk encryption: " + ("enabled" if s.get("encrypted") else "not detected")), False, False, 0)
    btn = Gtk.Button(label="Continue")
    btn.connect("clicked", lambda _: commit("encryption_status", {"disk_encryption": bool(s.get("encrypted"))}))
    box.pack_start(btn, False, False, 0)
    return box
