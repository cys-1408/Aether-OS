"""Language + keyboard layout selection.

Keyboard layouts are parsed from `localectl list-x11-keymap` (real output);
when localectl is unavailable the screen says so and offers the default 'us'
layout — it never invents a layout list.
"""

from __future__ import annotations

import subprocess

from ..installer_error import InstallerError
from .base_screen import ScreenBase


def list_keyboard_layouts() -> list[str] | None:
    try:
        proc = subprocess.run(
            ["localectl", "list-x11-keymap"], capture_output=True, timeout=15
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    if proc.returncode != 0:
        return None
    layouts = [
        line.strip()
        for line in proc.stdout.decode("utf-8", errors="replace").splitlines()
        if line.strip()
    ]
    return layouts or None


def list_locales() -> list[str]:
    # Locales offered by the shipped language pack set (localization/po).
    from pathlib import Path

    yaml_candidates = [
        Path(__file__).resolve().parents[3] / "localization" / "locales" /
        "supported-locales.yaml",
        Path("/etc/aether/installer/supported-locales.yaml"),
    ]
    for path in yaml_candidates:
        if path.is_file():
            import yaml

            data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
            codes = [entry.get("code") for entry in data.get("locales", [])
                     if isinstance(entry, dict) and entry.get("code")]
            if codes:
                return codes
    return ["en_US.UTF-8"]


class LanguageKeyboardScreen(ScreenBase):
    title = "Language and keyboard"
    subtitle = "Choose the system language and keyboard layout."

    def _build_gtk(self):
        from gi.repository import Gtk

        box = self.gtk_box(spacing=12)
        box.pack_start(self.gtk_heading(), False, False, 0)

        locales = list_locales()
        grid = Gtk.Grid(column_spacing=12, row_spacing=8)

        grid.attach(Gtk.Label(label="Language", xalign=0.0), 0, 0, 1, 1)
        locale_combo = Gtk.ComboBoxText()
        for code in locales:
            locale_combo.append_text(code)
        current = str(self.controller.get("locale") or "en_US.UTF-8")
        if current in locales:
            locale_combo.set_active(locales.index(current))
        elif locales:
            locale_combo.set_active(0)
        grid.attach(locale_combo, 1, 0, 1, 1)

        grid.attach(Gtk.Label(label="Keyboard layout", xalign=0.0), 0, 1, 1, 1)
        layout_combo = Gtk.ComboBoxText()
        layouts = list_keyboard_layouts()
        self._layouts_live = layouts is not None
        if layouts:
            for code in layouts:
                layout_combo.append_text(code)
            current_layout = str(self.controller.get("keyboard_layout") or "us")
            if current_layout in layouts:
                layout_combo.set_active(layouts.index(current_layout))
            else:
                layout_combo.set_active(0)
        else:
            layout_combo.append_text("us")
            layout_combo.set_active(0)
        grid.attach(layout_combo, 1, 1, 1, 1)

        note = Gtk.Label(xalign=0.0)
        if not self._layouts_live:
            note.set_markup(
                "<span alpha='60%'>localectl list-x11-keymap unavailable; "
                "defaulting to 'us'</span>"
            )
        box.pack_start(grid, False, False, 0)
        box.pack_start(note, False, False, 0)

        locale_combo.connect("changed", self._on_locale)
        layout_combo.connect("changed", self._on_layout)
        self._locale_combo = locale_combo
        self._layout_combo = layout_combo
        return box

    def _on_locale(self, combo):
        if combo.get_active_text():
            self.controller.apply("locale", combo.get_active_text())

    def _on_layout(self, combo):
        if combo.get_active_text():
            self.controller.apply("keyboard_layout", combo.get_active_text())

    def run_cli(self) -> None:
        self.cli_header()
        locales = list_locales()
        locale = self.cli_choose("Language", locales)
        layouts = list_keyboard_layouts()
        if layouts is None:
            self.cli_print("localectl unavailable; keyboard layout defaults to 'us'")
            layout = "us"
        else:
            layout = self.cli_choose("Keyboard layout", layouts)
        self.controller.apply("locale", locale)
        self.controller.apply("keyboard_layout", layout)
