"""Account page: create the primary user via the account service path."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "services/account/account-service"))
import user_create  # noqa: E402


def create(username: str, full_name: str, password: str, admin: bool) -> dict:
    return user_create.create_user(username, full_name, password, admin)


def run_cli_prompt() -> dict:
    while True:
        username = input("Username: ").strip()
        try:
            user_create.validate_username(username)
            break
        except ValueError as e:
            print(f"  invalid: {e}")
    full_name = input("Full name: ").strip()
    import getpass
    while True:
        pw = getpass.getpass("Password: ")
        try:
            user_create.validate_password(pw)
            break
        except ValueError as e:
            print(f"  invalid: {e}")
    admin = (input("Administrator (wheel)? [Y/n]: ").strip().lower() != "n")
    result = create(username, full_name, pw, admin)
    print("user created" if result.get("ok") else f"FAILED: {result.get('error')} (create later via Settings)")
    return {"username": username, "admin": admin}


def gtk_widget(commit):
    import gi
    gi.require_version("Gtk", "3.0")
    from gi.repository import Gtk
    grid = Gtk.Grid(row_spacing=8, column_spacing=8)
    labels = [Gtk.Label(label=f) for f in ("Username", "Full name", "Password", "Confirm")]
    entries = {"username": Gtk.Entry(), "full_name": Gtk.Entry(),
               "password": Gtk.Entry(), "confirm": Gtk.Entry()}
    for pw_field in ("password", "confirm"):
        entries[pw_field].set_visibility(False)
    admin = Gtk.CheckButton(label="Administrator (wheel)")
    btn = Gtk.Button(label="Continue")

    def _next(_):
        pw = entries["password"].get_text()
        if pw != entries["confirm"].get_text():
            entries["confirm"].set_text("")
            return
        create(entries["username"].get_text().strip(), entries["full_name"].get_text(), pw, admin.get_active())
        commit("account", {"username": entries["username"].get_text().strip()})
    btn.connect("clicked", _next)
    for i, lab in enumerate(labels):
        grid.attach(lab, 0, i, 1, 1)
        grid.attach(list(entries.values())[i], 1, i, 1, 1)
    grid.attach(admin, 1, 4, 1, 1)
    grid.attach(btn, 1, 5, 1, 1)
    return grid
