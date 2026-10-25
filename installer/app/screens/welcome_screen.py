"""Welcome screen: conditions, install/live context, accept checkbox."""

from __future__ import annotations

from .base_screen import ScreenBase


class WelcomeScreen(ScreenBase):
    title = "Welcome to AetherOS"
    subtitle = (
        "This installer will guide you through installing AetherOS on this "
        "machine. Installation erases the target disk. You can exit at any "
        "point before the final confirmation."
    )

    def _build_gtk(self):
        from gi.repository import Gtk

        box = self.gtk_box(spacing=16)
        box.pack_start(self.gtk_heading(), False, False, 0)

        info = Gtk.Label(xalign=0.0)
        info.set_markup(
            "AetherOS is a local-first Linux desktop: your files, your model, "
            "your machine. No telemetry is collected, ever.\n\n"
            "Before continuing:\n"
            "  - Back up anything you need from the target disk.\n"
            "  - Keep the machine on AC power during installation."
        )
        info.set_line_wrap(True)
        box.pack_start(info, False, False, 0)

        check = Gtk.CheckButton(label="I understand installation erases the "
                                      "selected disk and I have backups")
        check.set_active(bool(self.controller.get("welcome_accepted")))
        check.connect("toggled", self._on_toggle)
        box.pack_start(check, False, False, 0)
        self._check = check
        return box

    def _on_toggle(self, check):
        self.controller.apply("welcome_accepted", check.get_active())

    def run_cli(self) -> None:
        self.cli_header()
        self.cli_print(self.subtitle)
        self.cli_print(
            "AetherOS is local-first: no telemetry, ever. Installation erases "
            "the selected disk."
        )
        accepted = self.cli_confirm(
            "I understand installation erases the selected disk and I have backups",
            default=False,
        )
        self.controller.apply("welcome_accepted", accepted)
