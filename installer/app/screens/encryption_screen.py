"""Encryption screen: LUKS2 passphrase with strength check + confirmation."""

from __future__ import annotations

from ..installer_controller import InstallerController
from .base_screen import ScreenBase


class EncryptionScreen(ScreenBase):
    title = "Disk encryption"
    subtitle = ("Encrypt the root filesystem with LUKS2. You will type the "
                "passphrase on every boot. If you lose it, the data is "
                "unrecoverable — there is no reset path.")

    def _build_gtk(self):
        from gi.repository import Gtk

        box = self.gtk_box(spacing=12)
        box.pack_start(self.gtk_heading(), False, False, 0)

        enable = Gtk.CheckButton(label="Encrypt the root filesystem (LUKS2)")
        enable.set_active(bool(self.controller.get("encryption_enabled")))
        enable.connect("toggled", self._on_enable)
        box.pack_start(enable, False, False, 0)

        grid = Gtk.Grid(column_spacing=10, row_spacing=8, margin_start=20)
        grid.attach(Gtk.Label(label="Passphrase", xalign=0.0), 0, 0, 1, 1)
        pass_entry = Gtk.Entry()
        pass_entry.set_visibility(False)
        pass_entry.set_input_purpose(Gtk.InputPurpose.PASSWORD)
        grid.attach(pass_entry, 1, 0, 1, 1)
        grid.attach(Gtk.Label(label="Confirm", xalign=0.0), 0, 1, 1, 1)
        confirm_entry = Gtk.Entry()
        confirm_entry.set_visibility(False)
        confirm_entry.set_input_purpose(Gtk.InputPurpose.PASSWORD)
        grid.attach(confirm_entry, 1, 1, 1, 1)
        strength_label = Gtk.Label(xalign=0.0)
        grid.attach(strength_label, 0, 2, 2, 1)
        box.pack_start(grid, False, False, 0)
        grid.set_sensitive(enable.get_active())

        def refresh_strength(_entry=None):
            pw = pass_entry.get_text()
            if not pw:
                strength_label.set_text("")
                return
            strength = InstallerController.passphrase_strength(pw)
            if strength["acceptable"]:
                strength_label.set_markup(
                    f"<span foreground='#1a7f37'>strength: "
                    f"{'*' * strength['score']}{strength['score']}/4</span>")
            else:
                strength_label.set_markup(
                    "<span foreground='#b3261e'>"
                    + "; ".join(strength["problems"]) + "</span>")

        def apply_entries(_entry=None):
            self.controller.apply("luks_passphrase", pass_entry.get_text())
            self.controller.apply("luks_passphrase_confirm",
                                  confirm_entry.get_text())
            refresh_strength()

        pass_entry.connect("changed", apply_entries)
        confirm_entry.connect("changed", apply_entries)

        def on_enable(check):
            grid.set_sensitive(check.get_active())
            self.controller.apply("encryption_enabled", check.get_active())

        self._enable = enable
        self._grid = grid
        return box

    def _on_enable(self, check):
        self.controller.apply("encryption_enabled", check.get_active())

    def run_cli(self) -> None:
        self.cli_header()
        enabled = self.cli_confirm("Encrypt the root filesystem with LUKS2?",
                                   default=True)
        self.controller.apply("encryption_enabled", enabled)
        if not enabled:
            return
        while True:
            pw = self.cli_secret("LUKS2 passphrase")
            confirm = self.cli_secret("Confirm passphrase")
            if pw != confirm:
                self.cli_print("  passphrases do not match; try again")
                continue
            strength = InstallerController.passphrase_strength(pw)
            if not strength["acceptable"]:
                self.cli_print("  too weak: " + "; ".join(strength["problems"]))
                continue
            self.controller.apply("luks_passphrase", pw)
            self.controller.apply("luks_passphrase_confirm", confirm)
            self.cli_print(f"  strength: {strength['score']}/4")
            return
