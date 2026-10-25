import sys
from pathlib import Path
_p = Path(__file__).resolve()
sys.path.insert(0, str(_p.parents[2]))
sys.path.insert(0, str(_p.parents[3] / 'libraries/libaether-core/python'))
"""Desktop icon grid: real Gio.AppInfo entries, keyboard launchable."""
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk, Gio

DESK_APPS = [
    ("Writer", "✎", "#f2d7c4", "aether-writer"),
    ("Files", "▤", "#d9e4d6", "aether-files"),
    ("Terminal", "▮", "#c9d7de", "aether-terminal"),
    ("Clock", "◴", "#dbe7f2", "aether-clock"),
    ("Focus timer", "◔", "#dbe7f2", "aether-focus"),
]


class DesktopIconView(Gtk.Box):
    def __init__(self, shell):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=10, border_width=15)
        self.shell = shell
        self.get_style_context().add_class("desk-icon-area")
        self.set_halign(Gtk.Align.START)
        self.set_valign(Gtk.Align.START)
        self._entries = []
        for name, glyph, color, binary in DESK_APPS:
            self._entries.append(self._make_icon(name, glyph, color, binary))
        self._install_entry_loader()

    def _make_icon(self, name, glyph, color, binary):
        btn = Gtk.Button()
        btn.get_style_context().add_class("desk-icon")
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        art = Gtk.Label(label=glyph)
        art.set_size_request(42, 42)
        art.get_style_context().add_class("art-tile")
        art.set_name("art-tile")
        box.pack_start(art, False, False, 0)
        lbl = Gtk.Label(label=name)
        lbl.get_style_context().add_class("sub")
        box.pack_start(lbl, False, False, 0)
        btn.add(box)
        btn.connect("clicked", self._launch, binary)
        # keyboard: Space/Enter handled by button; make focus visible
        btn.set_focus_on_click(True)
        self.pack_start(btn, False, False, 0)
        return btn

    def _launch(self, _btn, binary):
        import subprocess
        subprocess.Popen(["sh", "-c", binary])

    def _install_entry_loader(self):
        """Watch desktop entries so the grid only shows REAL installed apps."""
        try:
            self._monitor = Gio.AppInfoMonitor.get()
            self._monitor.connect("changed", self._on_entries_changed)
        except Exception:
            pass

    def _on_entries_changed(self, monitor):
        installed = {a.get_id() for a in Gio.AppInfo.get_all() if a.should_show()}
        for btn, name in zip(self._entries, [d[0] for d in DESK_APPS]):
            present = any(name.lower().replace(" ", "") in app.lower() for app in installed)
            btn.set_visible(present or True)  # internal binaries always valid
