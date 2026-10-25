"""Timezone page via timedatectl."""
from __future__ import annotations

import subprocess


def timezones() -> list[str]:
    try:
        out = subprocess.run(["timedatectl", "list-timezones"], capture_output=True, text=True, timeout=10)
        return [l.strip() for l in out.stdout.splitlines() if l.strip()]
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return ["UTC"]


def current() -> str:
    try:
        out = subprocess.run(["timedatectl", "show", "-p", "Timezone", "--value"],
                             capture_output=True, text=True, timeout=5)
        return out.stdout.strip() or "UTC"
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return "UTC"


def set_timezone(tz: str) -> dict:
    if tz not in timezones():
        return {"ok": False, "error": f"unknown timezone: {tz}"}
    try:
        subprocess.run(["timedatectl", "set-timezone", tz], check=True, timeout=15)
        return {"ok": True, "timezone": tz}
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
        return {"ok": False, "error": str(e)}


def run_cli_prompt() -> dict:
    cur = current()
    print(f"Current timezone: {cur}")
    tz = input("Timezone (e.g. Asia/Kolkata, blank to keep): ").strip() or cur
    set_timezone(tz)
    return {"timezone": tz}


def gtk_widget(commit):
    import gi
    gi.require_version("Gtk", "3.0")
    from gi.repository import Gtk
    box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
    entry = Gtk.Entry()
    entry.set_text(current())
    entry.set_placeholder_text("Region/City")
    box.pack_start(entry, False, False, 0)
    btn = Gtk.Button(label="Continue")

    def _next(_):
        set_timezone(entry.get_text() or "UTC")
        commit("timezone", {"timezone": entry.get_text()})
    btn.connect("clicked", _next)
    box.pack_start(btn, False, False, 0)
    return box
