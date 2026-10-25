"""User account screen: username, full name, password twice, wheel checkbox."""

from __future__ import annotations

from .base_screen import ScreenBase

USERNAME_HELP = ("Lowercase, starts with a letter or underscore, then letters, "
                 "digits, '-' or '_'; up to 32 characters.")


def username_problem(raw: str) -> str | None:
    import re

    if not re.match(r"^[a-z_][a-z0-9_-]{0,31}$", raw):
        return USERNAME_HELP
    return None


class UserAccountScreen(ScreenBase):
    title = "Your account"
    subtitle = ("Create the primary user. It can be granted administrator "
                "(wheel) rights, requested via polkit when needed.")

    def _build_gtk(self):
        from gi.repository import Gtk

        box = self.gtk_box(spacing=12)
        box.pack_start(self.gtk_heading(), False, False, 0)

        grid = Gtk.Grid(column_spacing=10, row_spacing=8)
        grid.attach(Gtk.Label(label="Username", xalign=0.0), 0, 0, 1, 1)
        username = Gtk.Entry()
        username.set_text(str(self.controller.get("username") or ""))
        grid.attach(username, 1, 0, 1, 1)

        grid.attach(Gtk.Label(label="Full name", xalign=0.0), 0, 1, 1, 1)
        full_name = Gtk.Entry()
        full_name.set_text(str(self.controller.get("full_name") or ""))
        grid.attach(full_name, 1, 1, 1, 1)

        grid.attach(Gtk.Label(label="Password", xalign=0.0), 0, 2, 1, 1)
        password = Gtk.Entry()
        password.set_visibility(False)
        password.set_input_purpose(Gtk.InputPurpose.PASSWORD)
        grid.attach(password, 1, 2, 1, 1)

        grid.attach(Gtk.Label(label="Confirm password", xalign=0.0), 0, 3, 1, 1)
        password2 = Gtk.Entry()
        password2.set_visibility(False)
        password2.set_input_purpose(Gtk.InputPurpose.PASSWORD)
        grid.attach(password2, 1, 3, 1, 1)

        wheel = Gtk.CheckButton(label="Grant administrator rights (wheel group)")
        wheel.set_active(bool(self.controller.get("wheel_enabled", True)))
        grid.attach(wheel, 0, 4, 2, 1)

        feedback = Gtk.Label(xalign=0.0)
        grid.attach(feedback, 0, 5, 2, 1)
        box.pack_start(grid, False, False, 0)

        help_label = Gtk.Label(xalign=0.0)
        help_label.set_markup(f"<span alpha='60%'>{USERNAME_HELP}</span>")
        box.pack_start(help_label, False, False, 0)

        def on_changed(_entry=None):
            self.controller.apply("username", username.get_text().strip())
            self.controller.apply("full_name", full_name.get_text().strip())
            self.controller.apply("user_password", password.get_text())
            self.controller.apply("user_password_confirm", password2.get_text())
            self.controller.apply("wheel_enabled", wheel.get_active())
            problems = self.controller.validate_step("user_account")
            if problems:
                feedback.set_markup(
                    "<span foreground='#b3261e'>" + "; ".join(problems) + "</span>")
            else:
                feedback.set_markup(
                    "<span foreground='#1a7f37'>looks good</span>")

        for widget in (username, full_name, password, password2):
            widget.connect("changed", on_changed)
        wheel.connect("toggled", on_changed)
        return box

    def run_cli(self) -> None:
        self.cli_header()
        username = self.cli_ask("Username", validator=username_problem)
        full_name = self.cli_ask("Full name")
        while True:
            pw = self.cli_secret("Password (min 8 chars)")
            pw2 = self.cli_secret("Confirm password")
            if pw != pw2:
                self.cli_print("  passwords do not match")
                continue
            if len(pw) < 8:
                self.cli_print("  password must be at least 8 characters")
                continue
            break
        wheel = self.cli_confirm("Grant administrator rights (wheel group)?",
                                 default=True)
        self.controller.apply("username", username)
        self.controller.apply("full_name", full_name)
        self.controller.apply("user_password", pw)
        self.controller.apply("user_password_confirm", pw2)
        self.controller.apply("wheel_enabled", wheel)
