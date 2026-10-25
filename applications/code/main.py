"""Aether Code — real editor buffer, project tree, highlighting, optional AI."""
from __future__ import annotations

import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[2]
for p in (REPO_ROOT / "libraries/libaether-core/python", REPO_ROOT / "applications/app-framework"):
    sys.path.insert(0, str(p))

from application_context import AetherApp  # noqa: E402
from app_launcher_protocol import parse_launcher_args  # noqa: E402
from aether_core.config import atomic_write_text  # noqa: E402

import gi  # noqa: E402
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Pango  # noqa: E402

try:
    gi.require_version("GtkSource", "3.0")
    from gi.repository import GtkSource
    HAS_SOURCE = True
except (ImportError, ValueError):
    HAS_SOURCE = False


KEYWORDS = {
    ".py": ("def|class|import|from|return|if|elif|else|for|while|try|except|with|as|yield|lambda|not|and|or|in|is|None|True|False", "#"),
    ".js": ("function|const|let|var|return|if|else|for|while|class|extends|import|export|async|await|null|undefined|true|false", "//"),
    ".c": ("int|char|void|return|if|else|for|while|struct|typedef|static|const|unsigned|sizeof|switch|case|break|continue", "//"),
}


class SyntaxHighlighter:
    """Regex tagger fallback when GtkSourceView is unavailable (real highlighting)."""

    def __init__(self, buf):
        self.buf = buf
        self.tags = {
            "kw": buf.create_tag("kw", foreground_pango="#c3a6ff"),
            "str": buf.create_tag("str", foreground_pango="#7ec699"),
            "com": buf.create_tag("com", foreground_pango="#6b7581"),
            "num": buf.create_tag("num", foreground_pango="#e9c9a7"),
        }

    def highlight(self, text: str, suffix: str):
        spec = KEYWORDS.get(suffix)
        self._clear()
        if not spec:
            return
        kw_pat, com_pat = spec
        for m in re.finditer(rf"\b({kw_pat})\b", text):
            self._apply(m.start(), m.end(), "kw")
        for m in re.finditer(r'"[^"\n]*"|\'[^\'\n]*\'', text):
            self._apply(m.start(), m.end(), "str")
        for m in re.finditer(rf"^{com_pat}.*$", text, re.M):
            self._apply(m.start(), m.end(), "com")
        for m in re.finditer(r"\b\d+(\.\d+)?\b", text):
            self._apply(m.start(), m.end(), "num")

    def _apply(self, start, end, tag):
        self.buf.apply_tag(self.tags[tag],
                           self.buf.get_iter_at_offset(start), self.buf.get_iter_at_offset(end))

    def _clear(self):
        for tag in self.tags.values():
            self.buf.remove_tag(tag, self.buf.get_start_iter(), self.buf.get_end_iter())


class CodeWindow(Gtk.Box):
    def __init__(self, app, open_path: str | None = None):
        super().__init__(orientation=Gtk.Orientation.HORIZONTAL, spacing=8, border_width=12)
        self.app = app
        self.file_path: Path | None = None
        self.dirty = False

        self.tree_store = Gtk.TreeStore(str, str)
        self.tree = Gtk.TreeView(model=self.tree_store)
        self.tree.append_column(Gtk.TreeViewColumn("Project", Gtk.CellRendererText(), text=0))
        self.tree.connect("row-activated", self._open_from_tree)
        tree_scroll = Gtk.ScrolledWindow()
        tree_scroll.set_size_request(170, -1)
        tree_scroll.add(self.tree)
        self.pack_start(tree_scroll, False, False, 0)

        right = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        bar = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        for label, cb in (("Open file", self._open_file), ("Open folder", self._open_folder),
                          ("Save", self._save), ("Find", self._find_replace)):
            b = Gtk.Button(label=label)
            b.get_style_context().add_class("btn" if label == "Save" else "soft")
            b.connect("clicked", cb)
            bar.pack_start(b, False, False, 0)
        self.assist = Gtk.Button(label="Explain selection (local AI)")
        self.assist.get_style_context().add_class("soft")
        self.assist.connect("clicked", self._explain)
        bar.pack_start(self.assist, False, False, 0)
        right.pack_start(bar, False, False, 0)

        if HAS_SOURCE:
            lang_mgr = GtkSource.LanguageManager.get_default()
            self.buffer = GtkSource.Buffer()
            self.view = GtkSource.View(buffer=self.buffer)
            self.view.set_show_line_numbers(True)
            self.view.set_highlight_current_line(True)
        else:
            self.buffer = Gtk.TextBuffer()
            self.view = Gtk.TextView(buffer=self.buffer)
            self.view.override_font(Pango.FontDescription("monospace 12"))
            self.highlighter = SyntaxHighlighter(self.buffer)
            self.buffer.connect("changed", self._on_changed)
        scroll = Gtk.ScrolledWindow()
        scroll.set_vexpand(True)
        scroll.add(self.view)
        right.pack_start(scroll, True, True, 0)

        self.status = Gtk.Label(label="no file", xalign=0)
        self.status.get_style_context().add_class("sub")
        right.pack_start(self.status, False, False, 0)
        self.pack_start(right, True, True, 0)

        if open_path:
            self._load(Path(open_path).expanduser())

    # ------------------------------------------------------------- buffer
    def _on_changed(self, buf):
        self.dirty = True
        if hasattr(self, "highlighter"):
            text = buf.get_text(buf.get_start_iter(), buf.get_end_iter(), True)
            suffix = self.file_path.suffix if self.file_path else ""
            self.highlighter.highlight(text, suffix)

    def _load(self, path: Path):
        try:
            text = path.read_text(errors="replace")
        except OSError as e:
            self.status.set_text(f"open failed: {e}")
            return
        self.buffer.set_text(text)
        self.file_path = path
        self.dirty = False
        self.status.set_text(f"{path.name} · {len(text):,} chars")
        if HAS_SOURCE:
            lang = GtkSource.LanguageManager.get_default().guess_language(str(path), None)
            self.buffer.set_language(lang)

    def _save(self, _btn=None):
        if not self.file_path:
            from desktop.dialogs.file_picker_adapter import choose_file
            path = choose_file(self.get_toplevel(), "Save file", save=True)
            if not path:
                return
            self.file_path = Path(path)
        text = self.buffer.get_text(self.buffer.get_start_iter(), self.buffer.get_end_iter(), True)
        try:
            atomic_write_text(self.file_path, text, mode=0o644)
            self.dirty = False
            self.status.set_text(f"saved {self.file_path.name}")
        except OSError as e:
            self.status.set_text(f"save failed: {e}")

    # ------------------------------------------------------------- project
    def _open_file(self, _btn):
        from desktop.dialogs.file_picker_adapter import choose_file
        path = choose_file(self.get_toplevel(), "Open file")
        if path:
            self._load(Path(path))

    def _open_folder(self, _btn):
        from desktop.dialogs.file_picker_adapter import choose_folder
        folder = choose_folder(self.get_toplevel(), "Open project folder")
        if not folder:
            return
        base = Path(folder)
        self.tree_store.clear()
        root = self.tree_store.append(None, [base.name, str(base)])
        self._fill_tree(root, base, depth=0)
        self.tree.expand_row(self.tree_store.get_path(root), False)

    def _fill_tree(self, parent, base: Path, depth: int):
        if depth > 3:
            return
        try:
            for p in sorted(base.iterdir(), key=lambda x: (x.is_file(), x.name)):
                if p.name.startswith("."):
                    continue
                row = self.tree_store.append(parent, [p.name + ("/" if p.is_dir() else ""), str(p)])
                if p.is_dir():
                    self._fill_tree(row, p, depth + 1)
        except PermissionError:
            pass

    def _open_from_tree(self, tree, path, column):
        val = self.tree_store[path]
        target = Path(val[1])
        if target.is_file():
            self._load(target)

    # ------------------------------------------------------------- utils
    def _find_replace(self, _btn):
        dlg = Gtk.Dialog(title="Find & Replace", transient_for=self.get_toplevel())
        dlg.add_button("Cancel", Gtk.ResponseType.CANCEL)
        ok = dlg.add_button("Replace all", Gtk.ResponseType.OK)
        grid = Gtk.Grid(row_spacing=6, column_spacing=6)
        find_e, repl_e = Gtk.Entry(), Gtk.Entry()
        grid.attach(Gtk.Label(label="Find:"), 0, 0, 1, 1); grid.attach(find_e, 1, 0, 1, 1)
        grid.attach(Gtk.Label(label="Replace:"), 0, 1, 1, 1); grid.attach(repl_e, 1, 1, 1, 1)
        dlg.get_content_area().pack_start(grid, False, False, 8)
        dlg.show_all()
        if dlg.run() == Gtk.ResponseType.OK:
            text = self.buffer.get_text(self.buffer.get_start_iter(), self.buffer.get_end_iter(), True)
            self.buffer.set_text(text.replace(find_e.get_text(), repl_e.get_text()))
        dlg.destroy()

    def _explain(self, _btn):
        import threading
        if not self.view.get_selection_bounds():
            self.status.set_text("select code first")
            return
        start, end = self.view.get_selection_bounds()
        code = self.buffer.get_text(start, end, True)

        def work():
            result = self.app.services.call("runtime", "Runtime.infer", {
                "request_id": f"code-{int(threading.time() if hasattr(threading,'time') else 0)}",
                "task_class": "code", "prompt": code[:4000], "max_tokens": 300, "timeout_s": 60})
            if result and result.get("text"):
                GLib_set(self.status, result["text"][:220])
            else:
                GLib_set(self.status, "assist unavailable: " + str((result or {}).get("error", "runtime down")))

        def GLib_set(label, text):
            __import__("gi.repository", fromlist=["GLib"]).GLib.idle_add(label.set_text, text[:220])
        threading.Thread(target=work, daemon=True).start()


class CodeApp(AetherApp):
    app_id = "org.aether.Apps.Code"
    title = "Code"

    def __init__(self, open_path=None):
        super().__init__()
        self.open_path = open_path

    def build_window(self):
        win = super().build_window()
        win.set_default_size(700, 480)
        win.add(CodeWindow(self, self.open_path))
        return win


if __name__ == "__main__":
    args = parse_launcher_args(sys.argv[1:])
    sys.exit(CodeApp(open_path=args["open_path"]).run(sys.argv))
