"""Aether Writer — real documents, autosave drafts, recovery, optional AI."""
from __future__ import annotations

import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[2]
for p in (REPO_ROOT / "libraries/libaether-core/python", REPO_ROOT / "applications/app-framework"):
    sys.path.insert(0, str(p))

from application_context import AetherApp  # noqa: E402
from app_launcher_protocol import parse_launcher_args  # noqa: E402
from aether_core.config import atomic_write_text  # noqa: E402
from aether_core import paths  # noqa: E402

import gi  # noqa: E402
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GLib  # noqa: E402

DRAFTS = paths.USER_STATE_DIR / "drafts"


class WriterWindow(Gtk.Box):
    def __init__(self, app, open_path: str | None = None):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=8, border_width=14)
        self.app = app
        self.doc_path: Path | None = Path(open_path).expanduser() if open_path else None
        self.dirty = False
        self._check_recovery()

        bar = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        for label, cb in (("New", self._new), ("Open", self._open), ("Save", self._save), ("Save as…", self._save_as)):
            b = Gtk.Button(label=label)
            b.get_style_context().add_class("btn" if label == "Save" else "soft")
            b.connect("clicked", cb)
            bar.pack_start(b, False, False, 0)
        self.title_lbl = Gtk.Label(label="untitled", xalign=0)
        self.title_lbl.get_style_context().add_class("fpath")
        bar.pack_start(self.title_lbl, True, True, 0)
        self.pack_start(bar, False, False, 0)

        self.eyebrow = Gtk.Label(label="WRITER", xalign=0)
        self.eyebrow.get_style_context().add_class("eyebrow")
        self.pack_start(self.eyebrow, False, False, 0)

        self.view = Gtk.TextView(wrap_mode=Gtk.WrapMode.WORD)
        self.view.get_buffer().connect("changed", self._mark_dirty)
        scroll = Gtk.ScrolledWindow()
        scroll.set_vexpand(True)
        scroll.add(self.view)
        self.pack_start(scroll, True, True, 0)

        assist_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        summarize = Gtk.Button(label="Summarize (local AI)")
        summarize.get_style_context().add_class("soft")
        summarize.connect("clicked", self._summarize)
        assist_row.pack_start(summarize, False, False, 0)
        self.assist_note = Gtk.Label(label="", xalign=0)
        self.assist_note.get_style_context().add_class("sub")
        assist_row.pack_start(self.assist_note, True, True, 0)
        self.pack_start(assist_row, False, False, 0)

        self.status = Gtk.Label(label="ready", xalign=0)
        self.status.get_style_context().add_class("sub")
        self.pack_start(self.status, False, False, 0)

        if self.doc_path and self.doc_path.exists():
            self._load(self.doc_path)
        GLib.timeout_add_seconds(30, self._autosave)

    # ------------------------------------------------------------ doc ops
    def _mark_dirty(self, buf):
        self.dirty = True

    def _load(self, path: Path):
        try:
            self.view.get_buffer().set_text(path.read_text(errors="replace"))
            self.doc_path = path
            self.title_lbl.set_text(str(path))
            self.dirty = False
            self.status.set_text(f"opened {path.name}")
        except OSError as e:
            self.status.set_text(f"open failed: {e}")

    def _save(self, _btn=None):
        if not self.doc_path:
            return self._save_as()
        text = self.view.get_buffer().get_text(
            self.view.get_buffer().get_start_iter(), self.view.get_buffer().get_end_iter(), True)
        try:
            atomic_write_text(self.doc_path, text, mode=0o644)
            self.dirty = False
            self.status.set_text(f"saved {self.doc_path.name} · {time.strftime('%H:%M:%S')}")
        except OSError as e:
            self.status.set_text(f"save failed: {e}")

    def _save_as(self, _btn=None):
        from desktop.dialogs.file_picker_adapter import choose_file
        path = choose_file(self.get_toplevel(), "Save document", save=True)
        if path:
            self.doc_path = Path(path)
            self._save()

    def _new(self, _btn=None):
        if self.dirty:
            self._autosave()
        self.view.get_buffer().set_text("")
        self.doc_path = None
        self.title_lbl.set_text("untitled")
        self.status.set_text("new document")

    def _open(self, _btn=None):
        from desktop.dialogs.file_picker_adapter import choose_file
        path = choose_file(self.get_toplevel(), "Open document")
        if path:
            self._load(Path(path))

    def _autosave(self):
        if self.dirty:
            DRAFTS.mkdir(parents=True, exist_ok=True)
            name = self.doc_path.name if self.doc_path else f"untitled-{int(time.time())}.md"
            text = self.view.get_buffer().get_text(
                self.view.get_buffer().get_start_iter(), self.view.get_buffer().get_end_iter(), True)
            atomic_write_text(DRAFTS / name, text)
            self.status.set_text(f"autosaved draft · {time.strftime('%H:%M:%S')}")
            self.dirty = True  # autosave is a draft; doc stays dirty until Save
        return True

    def _check_recovery(self):
        if DRAFTS.exists() and any(DRAFTS.iterdir()):
            self.recovered = sorted(DRAFTS.glob("*"))
        else:
            self.recovered = []

    def _summarize(self, _btn):
        import threading
        text = self.view.get_buffer().get_text(
            self.view.get_buffer().get_start_iter(), self.view.get_buffer().get_end_iter(), True)
        if not text.strip():
            self.assist_note.set_text("nothing to summarize")
            return

        def work():
            result = self.app.services.call("runtime", "Runtime.infer", {
                "request_id": f"writer-{int(time.time())}", "task_class": "summarize",
                "prompt": text[:6000], "max_tokens": 200, "timeout_s": 60})
            if result and result.get("text"):
                GLib.idle_add(self.assist_note.set_text, result["text"][:300])
            else:
                reason = (result or {}).get("error", {}).get("message") if result else "AI runtime unavailable"
                GLib.idle_add(self.assist_note.set_text, f"summarize unavailable: {reason}")
        threading.Thread(target=work, daemon=True).start()


class WriterApp(AetherApp):
    app_id = "org.aether.Apps.Writer"
    title = "Writer"

    def __init__(self, open_path=None):
        super().__init__()
        self.open_path = open_path

    def build_window(self):
        win = super().build_window()
        win.add(WriterWindow(self, self.open_path))
        return win


if __name__ == "__main__":
    args = parse_launcher_args(sys.argv[1:])
    sys.exit(WriterApp(open_path=args["open_path"]).run(sys.argv))
