"""Privacy page: write user overrides of /etc/aether/privacy-defaults.yaml."""
from __future__ import annotations

from pathlib import Path

from aether_core.config import atomic_write_yaml


def run_cli_prompt() -> dict:
    print("Defaults: everything stays on this device; no telemetry; no accounts.")
    clip = input("Enable clipboard history? [y/N]: ").strip().lower() == "y"
    mic = input("Allow microphone by default? [y/N]: ").strip().lower() == "y"
    choices = {"clipboard_history": clip, "microphone_default": "allowed" if mic else "denied"}
    atomic_write_yaml(Path.home() / ".config/aether/privacy-user.yaml", {
        "clipboard": {"history_enabled": clip},
        "microphone": {"default": "allowed" if mic else "denied"},
    })
    return choices


def gtk_widget(commit):
    import gi
    gi.require_version("Gtk", "3.0")
    from gi.repository import Gtk
    box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
    note = Gtk.Label(label="Aether is local-first: no telemetry, no accounts.\n"
                           "Your files, model downloads and history stay on this device.")
    note.set_line_wrap(True)
    clip = Gtk.CheckButton(label="Clipboard history")
    mic = Gtk.CheckButton(label="Microphone allowed by default")
    btn = Gtk.Button(label="Continue")

    def _next(_):
        atomic_write_yaml(Path.home() / ".config/aether/privacy-user.yaml", {
            "clipboard": {"history_enabled": clip.get_active()},
            "microphone": {"default": "allowed" if mic.get_active() else "denied"},
        })
        commit("privacy", {"clipboard_history": clip.get_active(),
                           "microphone_default": "allowed" if mic.get_active() else "denied"})
    btn.connect("clicked", _next)
    for w in (note, clip, mic, btn):
        box.pack_start(w, False, False, 0)
    return box
