"""Users page: list + create via Accounts.* (polkit helper)."""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[2]
for p in (REPO_ROOT / "libraries/libaether-core/python", REPO_ROOT / "applications/app-framework"):
    sys.path.insert(0, str(p))

from application_context import AetherApp  # noqa: E402

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk


def build_page(app) -> Gtk.Box:
    box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8, border_width=16)
    users = app.services.call("account", "Accounts.list", {})
    if not users:
        box.pack_start(Gtk.Label(label="Account service unreachable", xalign=0), False, False, 0)
        return box
    for user in users.get("users", []):
        box.pack_start(Gtk.Label(label=f"{user['username']} ({user.get('full_name', '')}) · groups: {', '.join(user.get('groups', []))}", xalign=0), False, False, 0)
    btn = Gtk.Button(label="Create user…")
    btn.get_style_context().add_class("btn")
    btn.connect("clicked", _create, app)
    box.pack_start(btn, False, False, 0)
    return box


def _create(_btn, app):
    dlg = Gtk.Dialog(title="Create user", transient_for=None)
    dlg.add_button("Cancel", Gtk.ResponseType.CANCEL)
    dlg.add_button("Create", Gtk.ResponseType.OK)
    grid = Gtk.Grid(row_spacing=6, column_spacing=6)
    un, fn = Gtk.Entry(), Gtk.Entry()
    pw = Gtk.Entry(); pw.set_visibility(False)
    admin = Gtk.CheckButton(label="Administrator (wheel)")
    for i, (label, wd) in enumerate((("Username", un), ("Full name", fn), ("Password", pw))):
        grid.attach(Gtk.Label(label=label), 0, i, 1, 1)
        grid.attach(wd, 1, i, 1, 1)
    grid.attach(admin, 1, 3, 1, 1)
    dlg.get_content_area().pack_start(grid, False, False, 8)
    dlg.show_all()
    if dlg.run() == Gtk.ResponseType.OK:
        result = app.services.call("account", "Accounts.create", {
            "username": un.get_text().strip(), "full_name": fn.get_text(),
            "password": pw.get_text(), "admin": admin.get_active()})
        if result and not result.get("ok"):
            err = Gtk.MessageDialog(text=f"Create failed: {result.get('error')}", buttons=Gtk.ButtonsType.CLOSE)
            err.run(); err.destroy()
    dlg.destroy()
