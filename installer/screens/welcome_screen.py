"""Welcome screen (GTK)."""
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk


class WelcomeScreen(Gtk.Window):
    def __init__(self):
        super().__init__(title="Install Aether OS")
        self.set_default_size(560, 360)
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10, border_width=24)
        box.pack_start(Gtk.Label(label="Aether OS installer"), False, False, 0)
        box.pack_start(Gtk.Label(label="This will erase the target disk. You will confirm explicitly."), False, False, 0)
        start = Gtk.Button(label="Begin installation")
        start.get_style_context().add_class("btn")
        start.connect("clicked", self._begin)
        box.pack_start(start, False, False, 0)
        self.add(box)

    def _begin(self, _btn):
        from installer_controller import InstallerController
        from installer_state import InstallerState
        Gtk.main_quit()
        controller = InstallerController(InstallerState())
        import subprocess, sys
        sys.exit(subprocess.call(["aether-installer", "--cli"]))
