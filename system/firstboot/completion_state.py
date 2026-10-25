"""Completion: finalize first-boot state."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))


def run_cli_prompt() -> dict:
    return {"completed": True}


def gtk_widget(commit):
    import gi
    gi.require_version("Gtk", "3.0")
    from gi.repository import Gtk
    box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
    box.pack_start(Gtk.Label(label="You're all set. Welcome to Aether!"), False, False, 0)
    btn = Gtk.Button(label="Finish")
    btn.connect("clicked", lambda _: commit("completion", {"completed": True}))
    box.pack_start(btn, False, False, 0)
    return box
