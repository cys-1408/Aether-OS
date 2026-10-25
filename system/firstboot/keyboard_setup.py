"""Keyboard page via localectl."""
from __future__ import annotations

import subprocess


def layouts() -> list[str]:
    try:
        out = subprocess.run(["localectl", "list-x11-keymap-layouts"], capture_output=True, text=True, timeout=10)
        return [l.strip() for l in out.stdout.splitlines() if l.strip()]
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return ["us"]


def set_layout(layout: str, variant: str | None = None) -> dict:
    argv = ["localectl", "set-x11-keymap", layout] + ([variant] if variant else [])
    try:
        subprocess.run(argv, check=True, timeout=15)
        return {"ok": True, "layout": layout}
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
        return {"ok": False, "error": str(e)}


def run_cli_prompt() -> dict:
    lay = layouts()
    for i, l in enumerate(lay[:30], 1):
        print(f"  {i}. {l}")
    choice = (input(f"Keyboard layout [1-{min(30, len(lay))}] (default 1): ").strip() or "1")
    layout = lay[int(choice) - 1]
    set_layout(layout)
    return {"keyboard_layout": layout}


def gtk_widget(commit):
    import gi
    gi.require_version("Gtk", "3.0")
    from gi.repository import Gtk
    box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
    combo = Gtk.ComboBoxText()
    for l in layouts():
        combo.append_text(l)
    combo.set_active(0)
    box.pack_start(combo, False, False, 0)
    btn = Gtk.Button(label="Continue")

    def _next(_):
        set_layout(combo.get_active_text() or "us")
        commit("keyboard", {"keyboard_layout": combo.get_active_text()})
    btn.connect("clicked", _next)
    box.pack_start(btn, False, False, 0)
    return box
