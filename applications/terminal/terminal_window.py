"""Aether Terminal window: real PTY sessions via Vte.Terminal or built-in renderer.

Both code paths are complete:
* VTE path — preferred when ``gi.repository.Vte`` is importable; full emulation,
  scrollback, clipboard, current-directory-uri tracking.
* Fallback path — a TextView output surface + styled prompt row driven by a
  real PTY (pty.fork), ANSI-stripped rendering, line-based input, search.
"""

from __future__ import annotations

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gdk, GLib, Gtk, Pango

try:
    gi.require_version("Vte", "2.91")
    from gi.repository import Vte

    VTE_AVAILABLE = True
except (ValueError, ImportError):
    Vte = None
    VTE_AVAILABLE = False

from copy_paste import handle_copy_paste_shortcut, paste_to_view
from pty_session import detect_shell
from resize_handler import ResizeCoordinator, terminal_font
from shell_process import ShellProcess
from terminal_history import TerminalHistory
from working_directory import WorkingDirectoryTracker


class TerminalPage(Gtk.Box):
    """Common page interface: process ownership, title, search, close."""

    def __init__(self, window: "TerminalWindow") -> None:
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self._window = window
        self.cwd_tracker = WorkingDirectoryTracker(
            getattr(window, "cwd_override", None)
        )

    def title(self) -> str:
        return self.cwd_tracker.prompt_text() or "shell"

    def search(self, term: str) -> int:
        return 0

    def shutdown(self) -> None:
        raise RuntimeError("TerminalPage subclasses must implement shutdown()")


class VteTerminalPage(TerminalPage):
    """Full VTE terminal bound to a real child shell."""

    def __init__(self, window: "TerminalWindow") -> None:
        super().__init__(window)
        self.terminal = Vte.Terminal()
        self.terminal.set_scrollback_lines(5000)
        self.terminal.set_font(terminal_font())
        self.terminal.set_colors(
            Gdk.RGBA(0.937, 0.89, 0.851, 1.0),          # #e9e3d9 fg
            Gdk.RGBA(0.149, 0.165, 0.188, 1.0),         # #262a30 bg
            [],
        )
        self.terminal.connect("child-exited", self._on_child_exited)
        self.terminal.connect("window-title-changed", self._on_title_changed)
        self.terminal.connect("current-directory-uri", self._on_dir_uri)
        self._exited = False
        self.pack_start(self.terminal, True, True, 0)
        self.terminal.connect("key-press-event", self._on_key_press)
        try:
            self._pid = self.terminal.spawn_sync(
                Vte.PtyFlags.DEFAULT,
                str(self.cwd_tracker.current),
                [detect_shell()],
                [],
                GLib.SpawnFlags.DO_NOT_REAP_CHILD | GLib.SpawnFlags.SEARCH_PATH,
                None,
                None,
            )
        except GLib.Error as exc:
            self._exited = True
            error_box = Gtk.Label(
                label=f"Failed to start shell: {exc.message}", xalign=0
            )
            error_box.set_margin_start(10)
            self.pack_start(error_box, False, False, 4)
            error_box.show_all()

    def _on_key_press(self, _widget, event):
        return handle_copy_paste_shortcut(
            event, self.terminal, lambda text: self.terminal.feed_child(text.encode())
        )

    def _on_child_exited(self, _terminal, _status):
        self._exited = True
        self._window.refresh_tab_label(self)

    def _on_title_changed(self, _terminal):
        self._window.refresh_tab_label(self)

    def _on_dir_uri(self, _terminal, _uri):
        if _uri:
            tracker_update = self.cwd_tracker.feed(
                f"\x1b]7;{_uri}\x07".encode()
            )
            if tracker_update:
                self._window.refresh_tab_label(self)

    def search(self, term: str) -> int:
        if not term:
            self.terminal.search_set_regex(None, 0)
            return 0
        regex = GLib.Regex.new(term, GLib.RegexCompileFlags.CASELESS, 0)
        vte_regex = Vte.Regex.new_for_search(term, -1, 0)
        self.terminal.search_set_regex(vte_regex, 0)
        self.terminal.search_set_wrap_around(True)
        self.terminal.search_find_next()
        del regex
        return 1

    def shutdown(self) -> None:
        if self._exited:
            return
        try:
            pid = self.terminal.get_property("child_pid")
            if pid:
                ShellProcess.kill_tree(int(pid))
        except (TypeError, ValueError):
            pass

    def has_process(self) -> bool:
        return not self._exited


class FallbackTerminalPage(TerminalPage):
    """TextView renderer over a raw PTY with a styled prompt input row."""

    def __init__(self, window: "TerminalWindow") -> None:
        super().__init__(window)
        self._command_history: list = []
        self._history_index = 0
        self._exited = False

        self._output = Gtk.TextView()
        self._output.set_editable(False)
        self._output.set_cursor_visible(False)
        self._output.set_wrap_mode(Gtk.WrapMode.CHAR)
        self._output.set_monospace(True)
        self._output.set_left_margin(10)
        self._output.set_right_margin(10)
        self._output.set_top_margin(8)
        self._output.set_bottom_margin(8)
        output_scroll = Gtk.ScrolledWindow()
        output_scroll.add(self._output)
        output_scroll.set_vexpand(True)
        self.pack_start(output_scroll, True, True, 0)

        prompt_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6, margin=6)
        self._prompt_label = Gtk.Label(label=self.cwd_tracker.prompt_text() + " $", xalign=0)
        self._prompt_label.set_monospace(True)
        self._input = Gtk.Entry()
        self._input.set_can_focus(True)
        self._input.connect("activate", self._on_activate)
        self._input.connect("key-press-event", self._on_input_key)
        prompt_row.pack_start(self._prompt_label, False, False, 0)
        prompt_row.pack_start(self._input, True, True, 0)
        self.pack_start(prompt_row, False, False, 0)

        self.history = TerminalHistory(self._output)
        self.history.append("Aether terminal — fallback renderer (Vte not available).\n")
        self.history.append(f"Shell: {detect_shell()}\n\n")

        self.process = ShellProcess(
            cwd=str(self.cwd_tracker.current),
            on_output=self._on_pty_output,
            on_exit=self._on_pty_exit,
        )
        self._resizer = ResizeCoordinator(output_scroll, terminal_font(), self._on_resize)
        self._input.connect("key-press-event", self._on_global_key)
        GLib.idle_add(self._focus_input)

    # -- pty plumbing ---------------------------------------------------------------

    def _on_pty_output(self, data: bytes) -> None:
        def append():
            cwd = self.cwd_tracker.feed(data)
            if cwd:
                self._prompt_label.set_text(self.cwd_tracker.prompt_text() + " $")
            self.history.append_chunk(data)
            return GLib.SOURCE_REMOVE

        GLib.idle_add(append)

    def _on_pty_exit(self, code: int) -> None:
        def mark():
            self._exited = True
            self.history.append(f"\n[process exited with code {code}]\n")
            self._window.refresh_tab_label(self)
            return GLib.SOURCE_REMOVE

        GLib.idle_add(mark)

    def _on_resize(self, cols: int, rows: int) -> None:
        if self.process.alive():
            self.process.resize(cols, rows)

    def _focus_input(self):
        self._input.grab_focus()
        return GLib.SOURCE_REMOVE

    # -- input -------------------------------------------------------------------------

    def _on_activate(self, entry):
        command = entry.get_text()
        entry.set_text("")
        if self.process.alive():
            self.process.write(command.encode() + b"\n")
        if command.strip():
            self._command_history.append(command)
            self._history_index = len(self._command_history)

    def _on_input_key(self, _entry, event):
        if event.keyval == Gdk.KEY_Up and self._command_history:
            self._history_index = max(0, self._history_index - 1)
            self._input.set_text(self._command_history[self._history_index])
            return True
        if event.keyval == Gdk.KEY_Down and self._command_history:
            self._history_index = min(len(self._command_history), self._history_index + 1)
            next_index = min(self._history_index, len(self._command_history) - 1)
            self._input.set_text(self._command_history[next_index]
                                 if next_index >= 0 else "")
            return True
        return False

    def _on_global_key(self, _widget, event):
        return handle_copy_paste_shortcut(
            event, self._output,
            lambda text: self.process.write(text.encode()) if self.process.alive() else None,
        )

    def search(self, term: str) -> int:
        return self.history.search(term)

    def shutdown(self) -> None:
        if self.process.alive():
            self.process.terminate()

    def has_process(self) -> bool:
        return self.process.alive()


class TerminalWindow(Gtk.ApplicationWindow):
    def __init__(self, app) -> None:
        super().__init__(application=app)
        self._app = app
        self.set_default_size(900, 560)
        header = app.make_titlebar(self, "Terminal", "PTY shell")
        app.attach_health_chip(header)

        outer = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.add(outer)

        toolbar = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6, margin=6)
        new_tab_btn = Gtk.Button(label="＋ New tab")
        new_tab_btn.get_style_context().add_class("btn-soft")
        new_tab_btn.connect("clicked", lambda _b: self.new_page())
        self._search_entry = Gtk.SearchEntry()
        self._search_entry.set_placeholder_text("Search scrollback")
        self._search_entry.connect("activate", self._on_search)
        self._search_next = Gtk.Button(label="Next hit ▶")
        self._search_next.get_style_context().add_class("btn-soft")
        self._search_next.connect("clicked", self._on_search_next)
        self._search_status = Gtk.Label(label="", xalign=0)
        self._search_status.get_style_context().add_class("aether-muted")
        toolbar.pack_start(new_tab_btn, False, False, 0)
        toolbar.pack_start(self._search_entry, True, True, 0)
        toolbar.pack_start(self._search_next, False, False, 0)
        toolbar.pack_start(self._search_status, False, False, 0)
        outer.pack_start(toolbar, False, False, 0)

        self.notebook = Gtk.Notebook()
        self.notebook.set_scrollable(True)
        outer.pack_start(self.notebook, True, True, 0)

        renderer_note = "VTE renderer" if VTE_AVAILABLE else "fallback renderer (Vte absent)"
        self._renderer_label = Gtk.Label(label=renderer_note, xalign=0)
        self._renderer_label.get_style_context().add_class("aether-muted")
        outer.pack_end(self._renderer_label, False, False, 2)

        self.connect("destroy", self._on_destroy)
        GLib.idle_add(self._first_page)

    def _first_page(self):
        self.new_page()
        return GLib.SOURCE_REMOVE

    def new_page(self) -> TerminalPage:
        page = VteTerminalPage(self) if VTE_AVAILABLE else FallbackTerminalPage(self)
        label_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=4)
        label = Gtk.Label(label=page.title())
        close_btn = Gtk.Button(label="×")
        close_btn.set_relief(Gtk.ReliefStyle.NONE)
        close_btn.connect("clicked", lambda _b: self.close_page(page))
        label_box.pack_start(label, False, False, 0)
        label_box.pack_start(close_btn, False, False, 0)
        label_box.show_all()
        self.notebook.append_page(page, label_box)
        self.notebook.set_tab_reorderable(page, True)
        self.notebook.set_current_page(-1)
        self.notebook.set_tab_label(page, label_box)
        self.notebook.set_tab_label_text(page, page.title())
        self._page_labels = getattr(self, "_page_labels", {})
        self._page_labels[page] = label
        self.refresh_tab_label(page)
        return page

    def refresh_tab_label(self, page: TerminalPage) -> None:
        suffix = "" if page.has_process() else " (exited)"
        self.notebook.set_tab_label_text(page, page.title() + suffix)
        labels = getattr(self, "_page_labels", {})
        if page in labels:
            labels[page].get_children()[0].set_text(page.title() + suffix)

    def close_page(self, page: TerminalPage) -> None:
        index = self.notebook.page_num(page)
        if index == -1:
            return
        page.shutdown()
        self.notebook.remove_page(index)
        labels = getattr(self, "_page_labels", {})
        labels.pop(page, None)
        if self.notebook.get_n_pages() == 0:
            self.new_page()

    def _on_search(self, entry):
        page = self.notebook.get_nth_page(self.notebook.get_current_page())
        if page is None:
            return
        term = entry.get_text().strip()
        count = page.search(term)
        if count:
            self._search_status.set_text(f"{count} hit(s) for “{term}”")
        else:
            self._search_status.set_text("No hits" if term else "")

    def _on_search_next(self, _button):
        page = self.notebook.get_nth_page(self.notebook.get_current_page())
        if isinstance(page, FallbackTerminalPage):
            page.history.jump_next_hit()

    def _on_destroy(self, _window):
        for index in range(self.notebook.get_n_pages()):
            page = self.notebook.get_nth_page(index)
            try:
                page.shutdown()
            except Exception:
                pass
