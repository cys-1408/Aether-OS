"""Audio page: volume, devices, mic mute — real Audio.* calls."""
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
from gi.repository import Gtk


def build_page(app) -> Gtk.Box:
    box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8, border_width=16)
    status = app.services.call("audio", "Audio.status", {})
    if not status:
        box.pack_start(Gtk.Label(label="Audio service unreachable — is PipeWire running?", xalign=0), False, False, 0)
        return box
    backend = status.get("backend", {})
    box.pack_start(Gtk.Label(label=f"Server: {backend.get('server', 'none')}", xalign=0), False, False, 0)
    vol_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
    vol_row.pack_start(Gtk.Label(label="Volume", xalign=0), False, False, 0)
    scale = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 0, 100, 5)
    scale.set_size_request(200, -1)
    scale.connect("value-changed", lambda sc: app.services.call(
        "audio", "Audio.set_volume", {"target": "sink", "percent": int(sc.get_value())}))
    vol_row.pack_start(scale, True, True, 0)
    box.pack_start(vol_row, False, False, 0)
    for sink in status.get("devices", {}).get("sinks", []):
        b = Gtk.Button(label=f"Use {sink['name'][:40]}")
        b.get_style_context().add_class("soft")
        b.connect("clicked", lambda _b, nid=sink["id"]: app.services.call(
            "audio", "Audio.set_default_sink", {"node_id": nid}))
        box.pack_start(b, False, False, 0)
    mic = Gtk.Button(label="Mute microphone")
    mic.get_style_context().add_class("soft")
    mic.connect("clicked", lambda _b: app.services.call("audio", "Audio.set_mic_muted", {"muted": True}))
    box.pack_start(mic, False, False, 0)
    return box
