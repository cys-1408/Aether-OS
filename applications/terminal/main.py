"""Aether Terminal — REAL PTY-backed shell (Vte preferred, stdlib fallback)."""
from __future__ import annotations

import os
import pty
import select
import signal
import sys
import threading
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[2]
for p in (REPO_ROOT / "libraries/libaether-core/python", REPO_ROOT / "applications/app-framework"):
    sys.path.insert(0, str(p))

from application_context import AetherApp  # noqa: E402

import gi  # noqa: E402
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GLib, Gdk  # noqa: E402

try:
    gi.require_version("Vte", "2.91")
    from gi.repository import Vte
    HAS_VTE = True
except (ImportError, ValueError):
    HAS_VTE = False


class StdlibTerminal(Gtk.Box):
    """Real forkpty terminal rendered into a TextView (no Vte dependency)."""

    def __init__(self):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=6, border_width=12)
        self.get_style_context().add_class("term")
        self.view = Gtk.TextView(editable=True, cursor_visible=True, wrap_mode=Gtk.WrapMode.CHAR)
        self.view.override_font(__import__("gi").repository.Pango.FontDescription("monospace 12")
                                if hasattr(__import__("gi").repository, "Pango") else None) \
            if False else None
        self.buf = self.view.get_buffer()
        scroll = Gtk.ScrolledWindow()
        scroll.set_vexpand(True)
        scroll.add(self.view)
        self.pack_start(scroll, True, True, 0)
        self.prompt_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        self.prompt_lbl = Gtk.Label(label=self._prompt_text())
        self.prompt_lbl.get_style_context().add_class("termprompt")
        self.entry = Gtk.Entry()
        self.entry.connect("activate", self._submit)
        self.prompt_row.pack_start(self.prompt_lbl, False, False, 0)
        self.prompt_row.pack_start(self.entry, True, True, 0)
        self.pack_start(self.prompt_row, False, False, 0)

        self.master, slave = pty.openpty()
        self.pid = os.fork()
        if self.pid == 0:  # child: exec the user's shell
            os.close(self.master)
            os.setsid()
            os.dup2(slave, 0); os.dup2(slave, 1); os.dup2(slave, 2)
            if slave > 2:
                os.close(slave)
            shell = os.environ.get("SHELL", "/bin/bash")
            os.execv(shell, [shell, "-i"])
            os._exit(127)
        os.close(slave)
        self._alive = True
        threading.Thread(target=self._reader, daemon=True).start()
        self.view.connect("key-press-event", self._on_key)
        self.entry.grab_focus()
        self.connect("destroy", self._kill)

    @staticmethod
    def _prompt_text() -> str:
        user = os.environ.get("USER", "user")
        return f"[{user}@aether {os.path.basename(os.getcwd())}]$"

    def _reader(self):
        while self._alive:
            try:
                r, _, _ = select.select([self.master], [], [], 0.5)
            except OSError:
                break
            if r:
                try:
                    data = os.read(self.master, 4096)
                except OSError:
                    break
                if not data:
                    break
                GLib.idle_add(self._append, data.decode(errors="replace"))

    def _append(self, text: str):
        end = self.buf.get_end_iter()
        self.buf.insert(end, text)
        self.view.scroll_to_iter(self.buf.get_end_iter(), 0.0, False, 0, 0)
        return False

    def _submit(self, entry):
        line = entry.get_text() + "\n"
        entry.set_text("")
        os.write(self.master, line.encode())

    def _on_key(self, view, event):
        # Ctrl+C / Ctrl+D pass through to the PTY
        if event.state & Gdk.ModifierType.CONTROL_MASK:
            if event.keyval == ord("c"):
                os.write(self.master, b"\x03")
                return True
            if event.keyval == ord("d"):
                os.write(self.master, b"\x04")
                return True
        return False

    def _kill(self, *_):
        self._alive = False
        try:
            os.kill(self.pid, signal.SIGHUP)
        except OSError:
            pass
        try:
            os.close(self.master)
        except OSError:
            pass


class TerminalWindow(Gtk.Box):
    def __init__(self):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        if HAS_VTE:
            term = Vte.Terminal()
            shell = os.environ.get("SHELL", "/bin/bash")
            term.spawn_sync(Vte.PtyFlags.DEFAULT, os.getcwd(), [shell],
                            [], GLib.SpawnFlags.DO_NOT_REAP_CHILD, None, None)
            self.pack_start(term, True, True, 0)
        else:
            self.pack_start(StdlibTerminal(), True, True, 0)


class TerminalApp(AetherApp):
    app_id = "org.aether.Apps.Terminal"
    title = "Terminal"

    def build_window(self):
        win = super().build_window()
        win.set_default_size(560, 400)
        win.get_style_context().add_class("term")
        win.add(TerminalWindow())
        return win


if __name__ == "__main__":
    sys.exit(TerminalApp().run(sys.argv))
