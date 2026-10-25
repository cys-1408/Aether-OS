"""Privacy options screen: mirrors /etc/aether/privacy-defaults.yaml choices.

Telemetry is permanently NONE and is not offered as a choice. The remaining
options are local-first toggles the user can relax or tighten; selections are
written to the installed system by BaseConfigurator.
"""

from __future__ import annotations

from pathlib import Path

import yaml

from .base_screen import ScreenBase

DEFAULTS_PATHS = (
    Path("/etc/aether/privacy-defaults.yaml"),
    Path(__file__).resolve().parents[3] / "security" / "privacy" /
    "local-first-defaults.yaml",
)

# option key -> (label, description, default)
PRIVACY_OPTIONS = {
    "index_home_files": (
        "Index my home folder for local search (IntentFS)",
        "Everything stays on this machine; nothing is uploaded.",
        True,
    ),
    "removable_drive_indexing": (
        "Index removable drives while mounted",
        "Names and metadata of files on USB drives enter the local index.",
        False,
    ),
    "model_download_consent": (
        "Allow downloading the local AI model after install",
        "The model runs locally via llama.cpp; downloads are verified by sha256.",
        True,
    ),
    "microphone_enabled": (
        "Enable microphone input for voice features",
        "Voice capture starts only when you press the mic control.",
        False,
    ),
    "backup_reminders": (
        "Show backup reminders",
        "A gentle timer suggests backing up your files.",
        True,
    ),
}


def load_privacy_defaults() -> dict:
    for path in DEFAULTS_PATHS:
        if path.is_file():
            try:
                data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
            except yaml.YAMLError:
                continue
            choices = data.get("default_choices")
            if isinstance(choices, dict):
                return choices
            return {k: v.get("default", dflt) if isinstance(v, dict) else dflt
                    for k, (label, desc, dflt) in PRIVACY_OPTIONS.items()
                    for v in [data.get(k, dflt)]}
    return {key: dflt for key, (_l, _d, dflt) in PRIVACY_OPTIONS.items()}


class PrivacyOptionsScreen(ScreenBase):
    title = "Privacy"
    subtitle = ("AetherOS collects no telemetry — this is fixed and auditable "
                "(see /etc/aether/privacy-defaults.yaml). The choices below "
                "control optional local features.")

    def _build_gtk(self):
        from gi.repository import Gtk

        box = self.gtk_box(spacing=10)
        box.pack_start(self.gtk_heading(), False, False, 0)

        telemetry = Gtk.Label(xalign=0.0)
        telemetry.set_markup(
            "<span foreground='#1a7f37' weight='bold'>Telemetry: NONE "
            "(built-in, cannot be enabled)</span>")
        box.pack_start(telemetry, False, False, 0)

        defaults = load_privacy_defaults()
        current = dict(defaults)
        current.update(self.controller.get("privacy_choices", {}))
        checks = {}
        for key, (label, description, _dflt) in PRIVACY_OPTIONS.items():
            check = Gtk.CheckButton(label=label)
            check.set_tooltip_text(description)
            check.set_active(bool(current.get(key)))
            check.connect("toggled", self._on_toggle)
            box.pack_start(check, False, False, 0)
            checks[key] = check

        self._checks = checks
        self._sync()
        return box

    def _collect(self) -> dict:
        return {key: check.get_active() for key, check in self._checks.items()}

    def _sync(self) -> None:
        self.controller.apply("privacy_choices", self._collect())

    def _on_toggle(self, _check):
        self._sync()

    def run_cli(self) -> None:
        self.cli_header()
        self.cli_print("Telemetry: NONE (built-in, cannot be enabled).")
        choices = dict(load_privacy_defaults())
        choices.update(self.controller.get("privacy_choices", {}))
        for key, (label, description, dflt) in PRIVACY_OPTIONS.items():
            choices[key] = self.cli_confirm(f"{label} — {description}",
                                            default=bool(choices.get(key, dflt)))
        self.controller.apply("privacy_choices", choices)
