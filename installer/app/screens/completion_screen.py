"""Completion screen: success report + reboot guidance."""

from __future__ import annotations

from .base_screen import ScreenBase


class CompletionScreen(ScreenBase):
    title = "Installation complete"
    subtitle = "AetherOS is installed and ready for its first boot."

    def _build_gtk(self):
        from gi.repository import Gtk

        box = self.gtk_box(spacing=12)
        box.pack_start(self.gtk_heading(), False, False, 0)
        body = Gtk.Label(xalign=0.0)
        body.set_markup(
            "AetherOS has been installed.\n\n"
            "Next steps after reboot:\n"
            "  1. Remove the installation media.\n"
            "  2. Unlock the disk (if encrypted) and log in.\n"
            "  3. The first-boot assistant finishes configuration."
        )
        body.set_line_wrap(True)
        box.pack_start(body, False, False, 0)

        report = Gtk.Label(xalign=0.0)
        report.set_markup("<span alpha='60%'>A full install report is available "
                          "at /run/aether/installer.log</span>")
        report.set_line_wrap(True)
        box.pack_start(report, False, False, 0)

        reboot = Gtk.Button(label="Reboot now")
        reboot.connect("clicked", self._on_reboot)
        box.pack_start(reboot, False, False, 0)
        return box

    def _on_reboot(self, _button):
        import subprocess

        subprocess.run(["systemctl", "reboot"], check=False)

    def run_cli(self) -> None:
        self.cli_header()
        self.cli_print("AetherOS has been installed.")
        self.cli_print("Remove the installation media and reboot.")
        if self.cli_confirm("Reboot now?", default=False):
            import subprocess

            subprocess.run(["systemctl", "reboot"], check=False)
