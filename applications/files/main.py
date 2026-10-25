"""Aether Files — real filesystem, trash, mounts, IntentFS search."""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[2]
for p in (REPO_ROOT / "libraries/libaether-core/python", REPO_ROOT / "applications/app-framework", REPO_ROOT / "desktop"):
    sys.path.insert(0, str(p))

from application_context import AetherApp  # noqa: E402
from app_launcher_protocol import parse_launcher_args  # noqa: E402
from aether_core import filesops  # noqa: E402
from aether_core.errors import IpcError  # noqa: E402

import gi  # noqa: E402
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gio, GLib  # noqa: E402


class FilesWindow(Gtk.Box):
    def __init__(self, app, open_path: str | None = None):
        super().__init__(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        self.app = app
        self.cwd = Path(open_path).expanduser() if open_path else Path.home()
        self.trash_mode = False
        self._build_sidebar()
        self._build_main()

    def _build_sidebar(self):
        side = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2, border_width=10)
        for label, path in (("Home", Path.home()), ("Documents", Path.home() / "Documents"),
                            ("Downloads", Path.home() / "Downloads"),
                            ("Pictures", Path.home() / "Pictures"),
                            ("Music", Path.home() / "Music"), ("Videos", Path.home() / "Videos")):
            b = Gtk.Button(label=label)
            b.get_style_context().add_class("flat")
            b.connect("clicked", self._go, path)
            side.pack_start(b, False, False, 0)
        trash_btn = Gtk.Button(label="Trash")
        trash_btn.get_style_context().add_class("flat")
        trash_btn.connect("clicked", lambda _b: self._show_trash())
        side.pack_start(trash_btn, False, False, 0)
        side.set_size_request(140, -1)
        self.pack_start(side, False, False, 0)

    def _build_main(self):
        right = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6, border_width=10)
        self.path_bar = Gtk.Label(label=str(self.cwd), xalign=0)
        self.path_bar.get_style_context().add_class("fpath")
        right.pack_start(self.path_bar, False, False, 0)

        search_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        self.search_entry = Gtk.Entry()
        self.search_entry.set_placeholder_text("Search (semantic via IntentFS when available)")
        self.search_entry.connect("activate", self._search)
        search_row.pack_start(self.search_entry, True, True, 0)
        right.pack_start(search_row, False, False, 0)

        self.status = Gtk.Label(label="", xalign=0)
        self.status.get_style_context().add_class("sub")
        right.pack_start(self.status, False, False, 0)

        self.model = Gtk.ListStore(str, str, str, str, object)  # name, kind, size, mtime, path
        self.tree = Gtk.TreeView(model=self.model)
        for i, title in enumerate(("Name", "Kind", "Size", "Modified")):
            cell = Gtk.CellRendererText()
            col = Gtk.TreeViewColumn(title, cell, text=i)
            col.set_sort_column_id(i)
            self.tree.append_column(col)
        self.tree.connect("row-activated", self._activate)
        scroll = Gtk.ScrolledWindow()
        scroll.set_vexpand(True)
        scroll.add(self.tree)
        right.pack_start(scroll, True, True, 0)

        actions = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        for label, cb in (("New folder", self._new_folder), ("Rename", self._rename),
                          ("Trash", self._trash), ("Restore", self._restore),
                          ("Metadata", self._metadata)):
            b = Gtk.Button(label=label)
            b.get_style_context().add_class("soft")
            b.connect("clicked", cb)
            actions.pack_start(b, False, False, 0)
        right.pack_start(actions, False, False, 0)
        self.pack_start(right, True, True, 0)
        self.refresh()

    # ------------------------------------------------------------ listing
    def refresh(self):
        self.model.clear()
        if self.trash_mode:
            self._fill_trash()
            return
        try:
            entries = sorted(self.cwd.iterdir(), key=lambda p: (p.is_file(), p.name.lower()))
        except (PermissionError, FileNotFoundError) as e:
            self.status.set_text(f"Cannot open {self.cwd}: {e}")
            return
        import datetime
        for entry in entries:
            try:
                st = entry.stat()
                size = "—" if entry.is_dir() else f"{st.st_size:,} B"
                mtime = datetime.datetime.fromtimestamp(st.st_mtime).strftime("%Y-%m-%d %H:%M")
                kind = "folder" if entry.is_dir() else (entry.suffix.lstrip(".") or "file")
                self.model.append([entry.name, kind, size, mtime, entry])
            except (PermissionError, OSError):
                continue
        self.path_bar.set_text(str(self.cwd))
        self.status.set_text(f"{len(entries)} items")

    def _fill_trash(self):
        self.path_bar.set_text("Trash")
        for item in filesops.list_trash():
            self.model.append([item["name"], "trashed", f"{item['size']:,} B",
                               item["deleted"], item])

    # ------------------------------------------------------------ navigation
    def _go(self, _btn, path: Path):
        self.trash_mode = False
        self.cwd = path
        self.refresh()

    def _activate(self, tree, path, column):
        if self.trash_mode:
            return
        row = self.model[path]
        target: Path = row[4]
        if target.is_dir():
            self.cwd = target
            self.refresh()
        else:
            self._open_path(target)

    def _open_path(self, target: Path):
        import subprocess
        try:
            subprocess.Popen(["gio", "open", str(target)])
            self.status.set_text(f"Opened {target.name}")
        except FileNotFoundError:
            self.status.set_text("gio not available to open files")

    # ------------------------------------------------------------ search
    def _search(self, entry):
        import threading
        query = entry.get_text().strip()
        if not query:
            self.trash_mode = False
            self.refresh()
            return

        def work():
            result = self.app.services.call("intentfs", "IntentFS.search", {"query": query})
            if result:
                items = result.get("results", [])
                note = "IntentFS semantic results"
            else:
                items = self._filename_search(query)
                note = "IntentFS unavailable — filename search only"
            GLib.idle_add(self._show_results, items, note)

        threading.Thread(target=work, daemon=True).start()

    def _filename_search(self, query: str) -> list[dict]:
        out = []
        for p in self.cwd.rglob(f"*{query}*"):
            if p.is_file() and len(out) < 50:
                out.append({"filename": p.name, "path": str(p), "reasons": ["filename match"]})
        return out

    def _show_results(self, items, note):
        self.model.clear()
        for item in items[:100]:
            concepts = item.get("record", {}).get("concepts") if item.get("record") else None
            extra = f" · concepts: {', '.join(concepts)}" if concepts else ""
            reasons = ", ".join(item.get("reasons", []))
            self.model.append([item.get("filename", "?"), f"{note}{extra}",
                               reasons, "", Path(item.get("path", "/dev/null"))])
        self.status.set_text(f"{len(items)} results · {note}")
        return False

    # ------------------------------------------------------------ operations
    def _selected(self) -> Path | None:
        sel = self.tree.get_selection()
        model, iter_ = sel.get_selected()
        return model[iter_][4] if iter_ else None

    def _new_folder(self, _btn):
        name = f"New Folder"
        target = self.cwd / name
        i = 2
        while target.exists():
            target = self.cwd / f"{name} {i}"
            i += 1
        try:
            target.mkdir()
            self.refresh()
        except OSError as e:
            self.status.set_text(f"Cannot create folder: {e}")

    def _rename(self, _btn):
        target = self._selected()
        if not target:
            return
        dlg = Gtk.Dialog(title="Rename", transient_for=self.get_toplevel())
        dlg.add_button("Cancel", Gtk.ResponseType.CANCEL)
        dlg.add_button("Rename", Gtk.ResponseType.OK)
        entry = Gtk.Entry()
        entry.set_text(target.name)
        dlg.get_content_area().pack_start(entry, False, False, 8)
        dlg.show_all()
        if dlg.run() == Gtk.ResponseType.OK and entry.get_text().strip():
            new = target.with_name(entry.get_text().strip())
            try:
                target.rename(new)
                self.refresh()
            except OSError as e:
                self.status.set_text(f"Rename failed: {e}")
        dlg.destroy()

    def _trash(self, _btn):
        target = self._selected()
        if not target:
            return
        try:
            filesops.trash(target)
            self.status.set_text(f"Moved to trash: {target.name}")
            self.refresh()
        except Exception as e:
            self.status.set_text(f"Trash failed: {e}")

    def _restore(self, _btn):
        target = self._selected()
        if not target:
            return
        try:
            result = filesops.restore(Path(target).name if not self.trash_mode else str(target))
            self.status.set_text(f"Restored to {result['restored_to']}"
                                 + (" (renamed — conflict)" if result.get("renamed_due_to_conflict") else ""))
            self.refresh()
        except Exception as e:
            self.status.set_text(f"Restore failed: {e}")

    def _metadata(self, _btn):
        import datetime
        target = self._selected()
        if not target:
            return
        st = target.stat()
        info = (f"{target.name}\nsize: {st.st_size:,} bytes\n"
                f"modified: {datetime.datetime.fromtimestamp(st.st_mtime)}\n"
                f"mode: {oct(st.st_mode & 0o777)}\nowner uid/gid: {st.st_uid}/{st.st_gid}")
        dlg = Gtk.MessageDialog(transient_for=self.get_toplevel(), modal=True,
                                message_type=Gtk.MessageType.INFO,
                                buttons=Gtk.ButtonsType.CLOSE, text="File metadata")
        dlg.format_secondary_text(info)
        dlg.run()
        dlg.destroy()


class FilesApp(AetherApp):
    app_id = "org.aether.Apps.Files"
    title = "Files"

    def __init__(self, open_path=None):
        super().__init__()
        self.open_path = open_path

    def build_window(self):
        win = super().build_window()
        win.set_default_size(640, 460)
        win.add(FilesWindow(self, self.open_path))
        return win


if __name__ == "__main__":
    args = parse_launcher_args(sys.argv[1:])
    sys.exit(FilesApp(open_path=args["open_path"]).run(sys.argv))
