"""Aether Files main window: sidebar, path bar, grid/list views, search, trash."""

from __future__ import annotations

from pathlib import Path

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gio, GLib, Gtk

from file_list_model import (
    COL_IS_DIR,
    COL_MTIME_STR,
    COL_NAME,
    COL_PATH,
    COL_PERMS,
    COL_SIZE_STR,
    FileListModel,
)
from file_metadata_view import FileMetadataView
from file_operations import FileOperations
from file_permissions_view import FilePermissionsView
from file_preview import FilePreview
from intentfs_search_panel import IntentFsSearchPanel
from navigation_sidebar import NavigationSidebar
from trash_view import TrashView

VIEW_LIST = "list"
VIEW_GRID = "grid"


class FilesWindow(Gtk.ApplicationWindow):
    def __init__(self, app) -> None:
        super().__init__(application=app)
        self._app = app
        self.set_default_size(1020, 680)
        app.make_titlebar(self, "Files", "Aether file manager")
        app.attach_health_chip(_header_of(self))
        self._ops = FileOperations(self, app.services)
        self._model = FileListModel()
        self._current_dir = Path.home()
        self._history = [self._current_dir]
        self._history_pos = 0
        self._show_hidden = False
        self._view_mode = VIEW_LIST
        self._monitor = None
        self._monitor_dir = None

        outer = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.add(outer)

        # -- toolbar row --------------------------------------------------------
        toolbar = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6, margin=6)
        self._back_btn = Gtk.Button(label="◀")
        self._back_btn.set_tooltip_text("Back")
        self._back_btn.connect("clicked", self._go_back)
        self._up_btn = Gtk.Button(label="▲")
        self._up_btn.set_tooltip_text("Parent folder")
        self._up_btn.connect("clicked", lambda _b: self.navigate(self._current_dir.parent))
        refresh_btn = Gtk.Button(label="⟳")
        refresh_btn.set_tooltip_text("Refresh")
        refresh_btn.connect("clicked", lambda _b: self.refresh())
        self._path_entry = Gtk.Entry()
        self._path_entry.set_hexpand(True)
        self._path_entry.connect("activate", self._on_path_entry)
        self._hidden_btn = Gtk.ToggleButton(label="Hidden")
        self._hidden_btn.set_tooltip_text("Show hidden files")
        self._hidden_btn.connect("toggled", self._on_hidden_toggled)
        self._view_btn = Gtk.Button(label="List")
        self._view_btn.set_tooltip_text("Toggle grid/list view")
        self._view_btn.connect("clicked", self._toggle_view_mode)
        new_folder_btn = Gtk.Button(label="New Folder")
        new_folder_btn.get_style_context().add_class("btn-soft")
        new_folder_btn.connect("clicked", self._on_new_folder)
        search_btn = Gtk.Button(label="Search")
        search_btn.get_style_context().add_class("btn-dark")
        search_btn.connect("clicked", self._open_search)
        for widget in (
            self._back_btn, self._up_btn, refresh_btn, self._path_entry,
            self._hidden_btn, self._view_btn, new_folder_btn, search_btn,
        ):
            toolbar.pack_start(widget, widget is self._path_entry, True, 0)
        outer.pack_start(toolbar, False, False, 0)

        # -- body: sidebar | stack | side panels --------------------------------
        body = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        outer.pack_start(body, True, True, 0)

        self._sidebar = NavigationSidebar(app.services)
        self._sidebar.connect("location-activated", self._on_location)
        body.pack_start(self._sidebar, False, False, 0)

        self._stack = Gtk.Stack()
        body.pack_start(self._stack, True, True, 0)

        # list view
        list_scroll = Gtk.ScrolledWindow()
        self._tree = Gtk.TreeView(model=self._model.sorted_model)
        self._tree.set_headers_visible(True)
        for title, col, width in (
            ("Name", COL_NAME, 260), ("Size", COL_SIZE_STR, 100),
            ("Modified", COL_MTIME_STR, 150), ("Permissions", COL_PERMS, 110),
        ):
            cell = Gtk.CellRendererText()
            cell.set_property("ellipsize", 3)
            column = Gtk.TreeViewColumn(title, cell, text=col)
            column.set_resizable(True)
            column.set_min_width(width)
            column.set_sort_column_id(col)
            self._tree.append_column(column)
        self._tree.connect("row-activated", self._on_row_activated)
        self._tree.connect("cursor-changed", self._on_selection_changed)
        self._tree.get_selection().set_mode(Gtk.SelectionMode.MULTIPLE)
        list_scroll.add(self._tree)
        self._stack.add_named(list_scroll, VIEW_LIST)

        # grid view (IconView over the same sorted model)
        self._icon_view = Gtk.IconView(model=self._model.sorted_model)
        self._icon_view.set_text_column(COL_NAME)
        self._icon_view.set_item_width(120)
        self._icon_view.connect("item-activated", self._on_item_activated)
        self._icon_view.connect("selection-changed", lambda _v: self._on_selection_changed())
        grid_scroll = Gtk.ScrolledWindow()
        grid_scroll.add(self._icon_view)
        self._stack.add_named(grid_scroll, VIEW_GRID)

        # trash page
        self._trash_view = TrashView(self, self._ops)
        self._trash_view.connect("trash-restored", self._on_restored)
        self._stack.add_named(self._trash_view, "trash")

        # search page
        self._search_panel = IntentFsSearchPanel(app.services, self)
        self._stack.add_named(self._search_panel, "search")

        # right side panel: preview + metadata tabs
        side_notebook = Gtk.Notebook()
        side_notebook.set_size_request(280, -1)
        self._preview = FilePreview()
        side_notebook.append_page(self._preview, Gtk.Label(label="Preview"))
        self._metadata = FileMetadataView()
        side_notebook.append_page(self._metadata, Gtk.Label(label="Metadata"))
        perms_btn = Gtk.Button(label="Change permissions…")
        perms_btn.get_style_context().add_class("btn-soft")
        perms_btn.set_margin_start(8)
        perms_btn.set_margin_end(8)
        perms_btn.set_margin_bottom(8)
        perms_btn.connect("clicked", self._on_open_permissions)
        side_notebook.append_page(self._build_perms_page(perms_btn), Gtk.Label(label="Permissions"))
        body.pack_end(side_notebook, False, False, 0)

        # context menu + actions row
        actions = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6, margin=6)
        copy_btn = Gtk.Button(label="Copy to…")
        copy_btn.get_style_context().add_class("btn-soft")
        copy_btn.connect("clicked", lambda _b: self._transfer(move=False))
        move_btn = Gtk.Button(label="Move to…")
        move_btn.get_style_context().add_class("btn-soft")
        move_btn.connect("clicked", lambda _b: self._transfer(move=True))
        rename_btn = Gtk.Button(label="Rename")
        rename_btn.get_style_context().add_class("btn-soft")
        rename_btn.connect("clicked", self._on_rename)
        trash_btn = Gtk.Button(label="Move to Trash")
        trash_btn.get_style_context().add_class("btn-dark")
        trash_btn.connect("clicked", self._on_trash_selected)
        for widget in (copy_btn, move_btn, rename_btn, trash_btn):
            actions.pack_start(widget, False, False, 0)
        outer.pack_start(actions, False, False, 0)

        # status bar
        self._status = Gtk.Label(label="", xalign=0)
        self._status.get_style_context().add_class("status-bar")
        outer.pack_end(self._status, False, False, 0)

        self.refresh()
        self._sidebar.refresh_drives()
        self._preview.clear()

    # -- helpers ----------------------------------------------------------------

    def _build_perms_page(self, button):
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8, margin=10)
        note = Gtk.Label(
            label="Octal mode, owner and group are read from stat(); "
                  "chmod is enabled when you own the file.",
            xalign=0,
        )
        note.set_line_wrap(True)
        note.get_style_context().add_class("aether-muted")
        box.pack_start(note, False, False, 0)
        box.pack_start(button, False, False, 0)
        box.show_all()
        return box

    # -- navigation ---------------------------------------------------------------

    def navigate(self, directory):
        directory = Path(directory).expanduser().resolve()
        if not directory.is_dir():
            self._status.set_text(f"Not a folder: {directory}")
            return
        self._current_dir = directory
        self._history = self._history[: self._history_pos + 1]
        self._history.append(directory)
        self._history_pos = len(self._history) - 1
        self._back_btn.set_sensitive(self._history_pos > 0)
        self._path_entry.set_text(str(directory))
        self._show_directory(directory)
        self._stack.set_visible_child_name(self._view_mode)

    def _show_directory(self, directory: Path) -> None:
        result = self._model.populate(directory, self._show_hidden)
        if not result.get("ok"):
            self._model.clear()
            self._model.append_error_row(result.get("error", "unreadable folder"))
            self._status.set_text(result.get("error", "unreadable folder"))
        else:
            self._status.set_text(
                f"{result.get('count', 0)} items — {directory}"
            )
        self._install_monitor(directory)

    def refresh(self) -> None:
        if self._stack.get_visible_child_name() == "trash":
            self._trash_view.refresh()
        else:
            self._show_directory(self._current_dir)

    def _go_back(self, _button):
        if self._history_pos > 0:
            self._history_pos -= 1
            self._current_dir = self._history[self._history_pos]
            self._path_entry.set_text(str(self._current_dir))
            self._show_directory(self._current_dir)

    def _on_path_entry(self, entry):
        self.navigate(entry.get_text())

    def _on_location(self, _sidebar, kind, target, _label):
        if kind == "trash":
            self._trash_view.refresh()
            self._stack.set_visible_child_name("trash")
            return
        self.navigate(target)

    def _on_hidden_toggled(self, toggle):
        self._show_hidden = toggle.get_active()
        self._show_directory(self._current_dir)

    def _toggle_view_mode(self, button):
        self._view_mode = VIEW_GRID if self._view_mode == VIEW_LIST else VIEW_LIST
        button.set_label("Grid" if self._view_mode == VIEW_LIST else "List")
        self._stack.set_visible_child_name(self._view_mode)

    # -- file monitors ---------------------------------------------------------------

    def _install_monitor(self, directory: Path) -> None:
        if self._monitor is not None:
            try:
                self._monitor.cancel()
            except Exception:
                pass
            self._monitor = None
        directory = Path(directory)
        if not directory.is_dir():
            return
        gio_file = Gio.File.new_for_path(str(directory))
        try:
            self._monitor = gio_file.monitor_directory(Gio.FileMonitorFlags.NONE, None)
            self._monitor_dir = directory
            self._monitor.connect("changed", self._on_monitor_changed)
        except GLib.Error:
            self._monitor = None

    def _on_monitor_changed(self, _monitor, _file, _other, _event):
        # Debounce rapid change bursts; refresh shows the true on-disk state.
        if getattr(self, "_monitor_pending", False):
            return
        self._monitor_pending = True

        def do_refresh():
            self._monitor_pending = False
            if Path(self._path_entry.get_text()) == self._monitor_dir:
                self._show_directory(self._monitor_dir)
            return GLib.SOURCE_REMOVE

        GLib.timeout_add(300, do_refresh)

    # -- activation / selection --------------------------------------------------------

    def _selected_paths(self):
        if self._stack.get_visible_child_name() == VIEW_LIST:
            model, rows = self._tree.get_selection().get_selected_rows()
            return [Path(model[tree_iter][COL_PATH]) for tree_iter in rows]
        return [Path(model[path][COL_PATH]) for path in self._icon_view.get_selected_items()
                for model in [self._icon_view.get_model()]]

    def _on_row_activated(self, _view, path, _column):
        model = self._tree.get_model()
        target = Path(model[path][COL_PATH])
        self._activate_path(target)

    def _on_item_activated(self, _view, path):
        model = self._icon_view.get_model()
        self._activate_path(Path(model[path][COL_PATH]))

    def _activate_path(self, target: Path):
        if target.is_dir():
            self.navigate(target)
            return
        launched = Gio.app_info_launch_default_for_uri(target.as_uri(), None)
        if not launched:
            self._status.set_text(f"No application associated with {target.name}")

    def _on_selection_changed(self, *_args):
        paths = self._selected_paths()
        if len(paths) == 1:
            self._preview.show_file(paths[0])
            self._metadata.show_file(paths[0])
            count = f"1 item selected — {paths[0].name}"
        elif paths:
            self._preview.clear(f"{len(paths)} items selected. Preview needs a single selection.")
            self._metadata.clear()
            count = f"{len(paths)} items selected"
        else:
            self._preview.clear()
            self._metadata.clear()
            count = "No selection"
        self._status.set_text(f"{count} — {self._current_dir}")

    # -- operations --------------------------------------------------------------------

    def _transfer(self, move: bool):
        paths = self._selected_paths()
        if not paths:
            self._status.set_text("Select items to copy or move first.")
            return
        chooser = Gtk.FileChooserDialog(
            title="Move to folder" if move else "Copy to folder",
            transient_for=self, action=Gtk.FileChooserAction.SELECT_FOLDER,
            buttons=("Cancel", Gtk.ResponseType.CANCEL, "Choose", Gtk.ResponseType.OK),
        )
        chooser.set_current_folder(str(self._current_dir))
        answer = chooser.run()
        dest = Path(chooser.get_filename() or "")
        chooser.destroy()
        if answer != Gtk.ResponseType.OK or not dest:
            return

        def done(result):
            self.refresh()
            self._status.set_text(
                "Transfer cancelled." if result == "cancelled" else "Transfer complete."
            )

        def fail(message):
            self._status.set_text(f"Transfer failed: {message}")
            error = Gtk.MessageDialog(
                transient_for=self, modal=True, message_type=Gtk.MessageType.ERROR,
                buttons=Gtk.ButtonsType.CLOSE, text="File transfer failed",
            )
            error.format_secondary_text(message)
            error.run()
            error.destroy()

        self._ops.transfer(paths, dest, move, done, fail)

    def _on_rename(self, _button):
        paths = self._selected_paths()
        if len(paths) != 1:
            self._status.set_text("Rename needs exactly one selection.")
            return
        path = paths[0]
        dialog = Gtk.Dialog(title="Rename", transient_for=self, modal=True)
        dialog.set_default_size(360, 100)
        entry = Gtk.Entry(text=path.name)
        entry.set_activates_default(True)
        dialog.get_content_area().pack_start(entry, False, False, 12)
        dialog.add_button("Cancel", Gtk.ResponseType.CANCEL)
        apply_btn = dialog.add_button("Rename", Gtk.ResponseType.OK)
        apply_btn.get_style_context().add_class("btn-orange")
        apply_btn.set_can_default(True)
        apply_btn.grab_default()
        dialog.get_content_area().show_all()
        answer = dialog.run()
        new_name = entry.get_text().strip()
        dialog.destroy()
        if answer != Gtk.ResponseType.OK or new_name == path.name:
            return
        try:
            self._ops.rename(path, new_name)
        except (OSError, ValueError) as exc:
            self._status.set_text(f"Rename failed: {exc}")
            return
        self.refresh()

    def _on_trash_selected(self, _button):
        paths = self._selected_paths()
        if not paths:
            self._status.set_text("Select items to move to Trash.")
            return
        confirm = Gtk.MessageDialog(
            transient_for=self, modal=True, message_type=Gtk.MessageType.QUESTION,
            buttons=Gtk.ButtonsType.OK_CANCEL,
            text=f"Move {len(paths)} item(s) to Trash?",
        )
        confirm.format_secondary_text("Items can be restored from the Trash sidebar page.")
        answer = confirm.run()
        confirm.destroy()
        if answer != Gtk.ResponseType.OK:
            return
        try:
            self._ops.move_to_trash(paths)
        except RuntimeError as exc:
            self._status.set_text(str(exc))
            return
        self.refresh()

    def _on_new_folder(self, _button):
        dialog = Gtk.Dialog(title="New folder", transient_for=self, modal=True)
        dialog.set_default_size(360, 100)
        entry = Gtk.Entry()
        entry.set_placeholder_text("Folder name")
        entry.set_activates_default(True)
        dialog.get_content_area().pack_start(entry, False, False, 12)
        dialog.add_button("Cancel", Gtk.ResponseType.CANCEL)
        create_btn = dialog.add_button("Create", Gtk.ResponseType.OK)
        create_btn.get_style_context().add_class("btn-orange")
        create_btn.set_can_default(True)
        create_btn.grab_default()
        dialog.get_content_area().show_all()
        answer = dialog.run()
        name = entry.get_text().strip()
        dialog.destroy()
        if answer != Gtk.ResponseType.OK or not name:
            return
        target = self._current_dir / name
        try:
            target.mkdir(parents=False, exist_ok=False)
        except OSError as exc:
            self._status.set_text(f"Folder creation failed: {exc}")
            return
        self.refresh()

    def _on_open_permissions(self, _button):
        paths = self._selected_paths()
        if len(paths) != 1:
            self._status.set_text("Permissions editor needs exactly one selection.")
            return
        dialog = FilePermissionsView(self, paths[0], on_applied=lambda _p: self.refresh())
        dialog.run()

    def _on_restored(self, _trash_view, restored_to):
        self._status.set_text(f"Restored to {restored_to}")
        self.refresh()

    def _open_search(self, _button):
        self._stack.set_visible_child_name("search")
        self._search_panel._entry.grab_focus()

    # -- launcher protocol ----------------------------------------------------------

    def open_paths(self, paths) -> None:
        for path in paths:
            path = Path(path)
            if path.is_dir():
                self.navigate(path)
            else:
                self._preview.show_file(path)
                self._metadata.show_file(path)
                parent = path.parent
                if parent.is_dir():
                    self._current_dir = parent
                    self._path_entry.set_text(str(parent))
                    self._show_directory(parent)

    # -- archive extraction entry (uses the guarded adapter) --------------------------

    def extract_archive_into(self, archive: Path, dest: Path, policy: str = "ask") -> dict:
        from archive_adapter import extract

        return extract(archive, dest, policy=policy,
                       conflict_reporter=lambda target: self._ask_extract_conflict(target))

    def _ask_extract_conflict(self, target: Path) -> str:
        dialog = Gtk.MessageDialog(
            transient_for=self, modal=True, message_type=Gtk.MessageType.QUESTION,
            buttons=Gtk.ButtonsType.OK_CANCEL, text=f"{target.name} already exists",
        )
        dialog.format_secondary_text("OK = overwrite, Cancel = skip this member.")
        answer = dialog.run()
        dialog.destroy()
        return "overwrite" if answer == Gtk.ResponseType.OK else "skip"


def _header_of(window: Gtk.ApplicationWindow) -> Gtk.HeaderBar:
    return window.get_titlebar()


# Home directory bootstrap for first run: ensure standard folders exist so the
# sidebar places are honest (they reflect real XDG locations).
def ensure_standard_dirs() -> None:
    for name in ("Documents", "Downloads", "Pictures", "Music", "Videos"):
        target = Path.home() / name
        if not target.exists():
            try:
                target.mkdir(parents=False, exist_ok=True)
            except OSError:
                pass
    screenshots = Path.home() / "Pictures" / "Screenshots"
    if not screenshots.exists():
        try:
            screenshots.mkdir(parents=True, exist_ok=True)
        except OSError:
            pass
