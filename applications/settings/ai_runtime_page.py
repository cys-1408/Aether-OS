"""AI Runtime page: profile, models, usage — real Runtime.* data."""
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
    label = Gtk.Label(label="loading runtime state…", xalign=0)
    label.get_style_context().add_class("sub")
    box.pack_start(label, False, False, 0)

    def refresh():
        data = app.services.call("runtime", "Runtime.status", {})
        models = app.services.call("runtime", "Runtime.models_list", {})
        if not data:
            label.set_text("AI runtime unreachable — Aether works fully without it.")
            return False
        lines = [f"state: {data.get('state', '?')}"]
        if data.get("backend"):
            lines.append(f"backend: {data['backend']}")
        for m in (models or {}).get("models", []):
            lines.append(f"model: {m.get('name')} ({m.get('size_gb', '?')}GB, {m.get('license', '?')})")
        GLib.idle_add(label.set_text, "\n".join(lines))
        return False
    import threading
    threading.Thread(target=refresh, daemon=True).start()
    return box
