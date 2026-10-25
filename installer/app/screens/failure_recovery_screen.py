"""Failure recovery screen: what failed, rollback status, next actions."""

from __future__ import annotations

from ...logging.export_log import export_log
from ...recovery.install_rollback import InstallRollback
from ...storage.encryption_setup import MAPPER_PATH
from ...storage.mount_plan import mountpoint_is_busy
from .base_screen import ScreenBase


class FailureRecoveryScreen(ScreenBase):
    title = "Installation failed"
    subtitle = ("The install transaction rolled back everything it had "
                "changed. Review the options below; nothing was left "
                "half-installed without notice.")

    def _build_gtk(self):
        from gi.repository import Gtk

        box = self.gtk_box(spacing=12)
        box.pack_start(self.gtk_heading(), False, False, 0)

        failure = self.controller.failure or {}
        error_label = Gtk.Label(xalign=0.0)
        code = failure.get("code", "unknown")
        message = failure.get("message", "no error recorded")
        error_label.set_markup(
            f"<span foreground='#b3261e' weight='bold'>[{_escape(code)}]</span> "
            + _escape(message))
        error_label.set_line_wrap(True)
        box.pack_start(error_label, False, False, 0)

        state = Gtk.Label(xalign=0.0)
        state.set_markup(
            f"/mnt mounted: <b>{mountpoint_is_busy(__import__('pathlib').Path('/mnt'))}</b> · "
            f"mapper open: <b>{__import__('pathlib').Path(MAPPER_PATH).exists()}</b>")
        box.pack_start(state, False, False, 0)

        for label_text, handler in (
            ("Export diagnostic bundle…", self._on_export),
            ("Clean up mounts and mapper now", self._on_cleanup),
            ("Start over", self._on_restart),
        ):
            button = Gtk.Button(label=label_text)
            button.connect("clicked", handler)
            box.pack_start(button, False, False, 0)
        return box

    def _on_export(self, _button):
        export_log(self._home() / "aether-install-log.tar.gz")

    def _on_cleanup(self, _button):
        executor = InstallRollback(dry_run=self.controller.dry_run)
        executor.rollback(
            disk_path=str(self.controller.get("target_disk") or "/dev/null"),
            table_backup=None,
            luks_created=bool(self.controller.get("encryption_enabled")),
            luks_partition=None,
        )

    def _on_restart(self, _button):
        self.controller.reset_to_welcome()

    @staticmethod
    def _home():
        from pathlib import Path

        return Path.home()

    def run_cli(self) -> None:
        self.cli_header()
        failure = self.controller.failure or {}
        self.cli_print(f"[{failure.get('code', 'unknown')}] "
                       f"{failure.get('message', 'no error recorded')}")
        self.cli_print("Options:")
        self.cli_print("  1) export diagnostic bundle")
        self.cli_print("  2) clean up mounts and mapper")
        self.cli_print("  3) start over")
        choice = self.cli_choose("Action", ["export", "cleanup", "restart"],
                                 default="restart")
        if choice == "export":
            path = export_log(self._home() / "aether-install-log.tar.gz")
            self.cli_print(f"bundle written to {path}")
        elif choice == "cleanup":
            executor = InstallRollback(dry_run=self.controller.dry_run)
            report = executor.rollback(
                disk_path=str(self.controller.get("target_disk") or "/dev/null"),
                table_backup=None,
                luks_created=bool(self.controller.get("encryption_enabled")),
                luks_partition=None,
            )
            self.cli_print(f"cleanup ok: {report['ok']}")
        else:
            self.controller.reset_to_welcome()


def _escape(text: str) -> str:
    return (text.replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;"))
