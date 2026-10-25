"""Timezone screen backed by `timedatectl list-timezones`."""

from __future__ import annotations

import subprocess

from .base_screen import ScreenBase


def list_timezones() -> list[str] | None:
    try:
        proc = subprocess.run(
            ["timedatectl", "list-timezones"], capture_output=True, timeout=15
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    if proc.returncode != 0:
        return None
    zones = [line.strip() for line in
             proc.stdout.decode("utf-8", errors="replace").splitlines()
             if line.strip()]
    return zones or None


class TimezoneScreen(ScreenBase):
    title = "Timezone"
    subtitle = "Pick the timezone for the installed system (from timedatectl)."

    def _build_gtk(self):
        from gi.repository import Gtk

        box = self.gtk_box(spacing=12)
        box.pack_start(self.gtk_heading(), False, False, 0)

        zones = list_timezones()
        self._zones = zones
        combo = Gtk.ComboBoxText()
        note = Gtk.Label(xalign=0.0)
        if zones:
            for zone in zones:
                combo.append_text(zone)
            current = str(self.controller.get("timezone") or "UTC")
            if current in zones:
                combo.set_active(zones.index(current))
            else:
                combo.set_active(zones.index("UTC")) if "UTC" in zones else combo.set_active(0)
            combo.connect("changed", self._on_changed)
        else:
            entry = Gtk.Entry()
            entry.set_text(str(self.controller.get("timezone") or ""))
            entry.connect("changed", self._on_entry)
            self._entry = entry
            combo.set_sensitive(False)
            note.set_markup(
                "<span alpha='60%'>timedatectl list-timezones unavailable; "
                "type a zone name such as Europe/Berlin</span>")
            box.pack_start(entry, False, False, 0)
        box.pack_start(combo, False, False, 0)
        box.pack_start(note, False, False, 0)
        self._combo = combo
        return box

    def _on_changed(self, combo):
        if combo.get_active_text():
            self.controller.apply("timezone", combo.get_active_text())

    def _on_entry(self, entry):
        self.controller.apply("timezone", entry.get_text())

    def run_cli(self) -> None:
        self.cli_header()
        zones = list_timezones()
        if zones is None:
            self.cli_print("timedatectl unavailable; enter the zone manually.")
            zone = self.cli_ask("Timezone (e.g. Europe/Berlin)")
        else:
            zone = self.cli_choose("Timezone", zones, default="UTC")
        self.controller.apply("timezone", zone)
