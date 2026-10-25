"""Aether Software Center — real pacman repo browse/install with signature status."""
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
from gi.repository import Gtk, GLib

from repository_browser import search_packages, installed_names
from signature_status import signature_summary
from install_transaction import install, uninstall


class SoftwareWindow(Gtk.Box):
    def __init__(self, app):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=8, border_width=12)
        self.app = app
        bar = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        self.search = Gtk.Entry()
        self.search.set_placeholder_text("Search packages…")
        self.search.connect("activate", lambda _e: self._load(self.search.get_text()))
        bar.pack_start(self.search, True, True, 0)
        sig = Gtk.Button(label="Signature status")
        sig.get_style_context().add_class("soft")
        sig.connect("clicked", self._sig)
        bar.pack_end(sig, False, False, 0)
        self.pack_start(bar, False, False, 0)

        self.model = Gtk.ListStore(str, str, str, bool)  # name, version, repo, installed
        self.tree = Gtk.TreeView(model=self.model)
        for i, title in enumerate(("Package", "Version", "Repo", "Installed")):
            cell = Gtk.CellRendererText()
            col = Gtk.TreeViewColumn(title, cell, text=i)
            col.set_sort_column_id(i)
            self.tree.append_column(col)
        scroll = Gtk.ScrolledWindow()
        scroll.set_vexpand(True)
        scroll.add(self.tree)
        self.pack_start(scroll, True, True, 0)

        actions = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        ins = Gtk.Button(label="Install…")
        ins.get_style_context().add_class("btn")
        ins.connect("clicked", self._install)
        rem = Gtk.Button(label="Remove…")
        rem.get_style_context().add_class("soft")
        rem.connect("clicked", self._remove)
        self.status = Gtk.Label(label="", xalign=0)
        self.status.get_style_context().add_class("sub")
        actions.pack_start(ins, False, False, 0)
        actions.pack_start(rem, False, False, 0)
        actions.pack_start(self.status, True, True, 0)
        self.pack_start(actions, False, False, 0)
        self._load("")

    def _load(self, query):
        import threading
        def work():
            pkgs = search_packages(query)
            installed = installed_names()
            GLib.idle_add(self._fill, pkgs, installed)
        threading.Thread(target=work, daemon=True).start()

    def _fill(self, pkgs, installed):
        self.model.clear()
        for p in pkgs[:200]:
            self.model.append([p["name"], p.get("version", ""), p.get("repo", ""), p["name"] in installed])
        return False

    def _selected(self):
        model, iter_ = self.tree.get_selection().get_selected()
        return model[iter_][0] if iter_ else None

    def _install(self, _btn):
        name = self._selected()
        if not name:
            return
        dlg = Gtk.MessageDialog(text=f"Install {name}?", secondary_text="Runs a real signed package transaction (pkexec aether-pm).",
                                buttons=Gtk.ButtonsType.OK_CANCEL)
        if dlg.run() == Gtk.ResponseType.OK:
            result = install(name)
            self.status.set_text(f"install: {result}")
        dlg.destroy()

    def _remove(self, _btn):
        name = self._selected()
        if not name:
            return
        dlg = Gtk.MessageDialog(text=f"Remove {name}?", secondary_text="This uninstalls the package.",
                                buttons=Gtk.ButtonsType.OK_CANCEL)
        if dlg.run() == Gtk.ResponseType.OK:
            result = uninstall(name)
            self.status.set_text(f"remove: {result}")
        dlg.destroy()

    def _sig(self, _btn):
        self.status.set_text(signature_summary())


class SoftwareCenterApp(AetherApp):
    app_id = "org.aether.Apps.SoftwareCenter"
    title = "Software Center"

    def build_window(self):
        win = super().build_window()
        win.set_default_size(560, 440)
        win.add(SoftwareWindow(self))
        return win


if __name__ == "__main__":
    sys.exit(SoftwareCenterApp().run(sys.argv))
