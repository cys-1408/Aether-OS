"""Install summary: full recap of every choice + typed disk confirmation."""

from __future__ import annotations

from ...storage.disk_discovery import disk_summary
from ..installer_error import GuardError
from .base_screen import ScreenBase


def recap_lines(controller) -> list[str]:
    lines = []
    lines.append(f"Language/locale : {controller.get('locale')}")
    lines.append(f"Keyboard        : {controller.get('keyboard_layout')}")
    mode = controller.get("network_mode")
    lines.append(f"Network         : {mode} install")
    lines.append(f"Target disk     : {disk_summary(controller.get('target_disk_info', {}))}")
    plan = controller.get("partition_plan", {})
    for part in plan.get("partitions", []):
        gib = part["size_bytes"] / 1024 ** 3
        enc = " (LUKS2)" if part.get("encrypted") else ""
        lines.append(f"  partition     : {part['role']} {gib:.1f} GiB "
                     f"{part['filesystem']} -> {part.get('mount')}{enc}")
    lines.append(f"Encryption      : {'LUKS2 enabled' if plan.get('encrypted') else 'disabled'}")
    lines.append(f"Timezone        : {controller.get('timezone')}")
    lines.append(f"User            : {controller.get('username')} "
                 f"(wheel: {'yes' if controller.get('wheel_enabled', True) else 'no'})")
    choices = controller.get("privacy_choices", {})
    for key in sorted(choices):
        lines.append(f"Privacy {key:<22}: {choices[key]}")
    return lines


class InstallSummaryScreen(ScreenBase):
    title = "Summary and confirmation"
    subtitle = ("Review every choice. To continue you must type the exact "
                "target disk device path below — this is the last warning.")

    def _build_gtk(self):
        from gi.repository import Gtk

        box = self.gtk_box(spacing=12)
        box.pack_start(self.gtk_heading(), False, False, 0)

        text = Gtk.Label(xalign=0.0)
        text.set_markup("<tt>" + "\n".join(
            _escape(line) for line in recap_lines(self.controller)
        ) + "</tt>")
        box.pack_start(text, False, False, 0)

        erase = Gtk.Label(xalign=0.0)
        disk = str(self.controller.get("target_disk"))
        erase.set_markup(
            "<span foreground='#b3261e' size='large' weight='bold'>"
            f"This will ERASE {disk}</span>")
        box.pack_start(erase, False, False, 0)

        grid = Gtk.Grid(column_spacing=10, row_spacing=8)
        grid.attach(Gtk.Label(label=f"Type {disk} to confirm", xalign=0.0),
                    0, 0, 1, 1)
        typed = Gtk.Entry()
        typed.set_placeholder_text(disk)
        grid.attach(typed, 1, 0, 1, 1)
        confirm = Gtk.CheckButton(label="I confirm all choices above")
        grid.attach(confirm, 0, 1, 2, 1)
        status = Gtk.Label(xalign=0.0)
        grid.attach(status, 0, 2, 2, 1)
        box.pack_start(grid, False, False, 0)

        def on_change(_widget=None):
            self.controller.apply("summary_confirmed", confirm.get_active())
            typed_name = typed.get_text().strip()
            if typed_name:
                try:
                    self.controller.arm_guard(typed_name)
                    status.set_markup(
                        "<span foreground='#1a7f37'>guard armed; plan hash "
                        f"{self.controller.plan_hash()[:12]}…</span>")
                except GuardError as exc:
                    status.set_markup(
                        f"<span foreground='#b3261e'>{_escape(exc.message)}</span>")
            on_change_ok = confirm.get_active()
            self.controller.apply("summary_confirmed", on_change_ok and
                                  self.controller.guard.armed)

        typed.connect("changed", on_change)
        confirm.connect("toggled", on_change)
        return box

    def run_cli(self) -> None:
        self.cli_header()
        for line in recap_lines(self.controller):
            self.cli_print(line)
        disk = str(self.controller.get("target_disk"))
        self.cli_print("")
        self.cli_print(f"*** THIS WILL ERASE {disk} ***")
        typed = self.cli_ask(f"Type the disk path ({disk}) to confirm")
        try:
            self.controller.arm_guard(typed)
        except GuardError as exc:
            self.cli_print(f"confirmation refused: {exc.message}")
            self.controller.apply("summary_confirmed", False)
            return
        confirmed = self.cli_confirm("Confirm all choices above", default=False)
        self.controller.apply("summary_confirmed", confirmed)


def _escape(text: str) -> str:
    return (text.replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;"))
