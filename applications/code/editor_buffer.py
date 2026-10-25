"""Editor buffer: GtkSourceView when available, plain TextBuffer otherwise.

Handles open/save with real dirty tracking and honest encoding errors.
"""

from __future__ import annotations

from pathlib import Path

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

try:
    gi.require_version("GtkSource", "3.0")
    from gi.repository import GtkSource

    GTKSOURCE_AVAILABLE = True
except (ValueError, ImportError):
    GtkSource = None
    GTKSOURCE_AVAILABLE = False

from app_framework.app_lifecycle import atomic_write_text
from language_support import language_for_path


class EditorOpenError(RuntimeError):
    pass


class EditorBuffer:
    """One open file: buffer + path + dirty flag + language."""

    MAX_OPEN_BYTES = 8 * 1024 * 1024

    def __init__(self) -> None:
        self.path: Path | None = None
        self.dirty = False
        self.on_disk_mtime = None
        self.is_gtksource = GTKSOURCE_AVAILABLE
        if GTKSOURCE_AVAILABLE:
            self.buffer = GtkSource.Buffer()
            self.buffer.set_highlight_matching_brackets(True)
        else:
            self.buffer = Gtk.TextBuffer()
        self._baseline = ""
        self.buffer.connect("changed", self._on_changed)

    # -- content -----------------------------------------------------------------

    def text(self) -> str:
        start, end = self.buffer.get_bounds()
        return self.buffer.get_text(start, end, True)

    def set_text(self, text: str) -> None:
        self.buffer.begin_not_undoable_action()
        self.buffer.set_text(text)
        self.buffer.end_not_undoable_action()
        self._baseline = text
        self.dirty = False
        if self.path is not None:
            try:
                self.on_disk_mtime = self.path.stat().st_mtime
            except OSError:
                self.on_disk_mtime = None

    def _on_changed(self, _buffer):
        self.dirty = self.text() != self._baseline

    # -- file IO -------------------------------------------------------------------

    def open_file(self, path: Path) -> None:
        path = Path(path).expanduser()
        if not path.is_file():
            raise EditorOpenError(f"No such file: {path}")
        size = path.stat().st_size
        if size > self.MAX_OPEN_BYTES:
            raise EditorOpenError(
                f"{path.name} is {size} bytes — the editor opens files up to "
                f"{self.MAX_OPEN_BYTES} bytes."
            )
        try:
            raw = path.read_bytes()
        except OSError as exc:
            raise EditorOpenError(f"Cannot read {path}: {exc}") from exc
        try:
            text = raw.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise EditorOpenError(
                f"{path.name} is not valid UTF-8 (byte offset {exc.start})."
            ) from exc
        self.path = path
        self.on_disk_mtime = path.stat().st_mtime
        self.set_text(text)
        self._configure_language()

    def save(self, path: Path | None = None) -> Path:
        target = Path(path) if path is not None else self.path
        if target is None:
            raise EditorOpenError("No file chosen — use Save As")
        self.changed_on_disk()  # raise before clobbering if needed
        try:
            atomic_write_text(target, self.text())
        except OSError as exc:
            raise EditorOpenError(f"Save failed: {exc}") from exc
        self.path = target
        self.on_disk_mtime = target.stat().st_mtime
        self._baseline = self.text()
        self.dirty = False
        self._configure_language()
        return target

    def changed_on_disk(self) -> bool:
        """True when the file's mtime moved since we loaded/saved it."""
        if self.path is None or self.on_disk_mtime is None:
            return False
        try:
            return self.path.stat().st_mtime != self.on_disk_mtime
        except OSError:
            return False

    def _configure_language(self) -> None:
        if not self.is_gtksource or self.path is None:
            return
        language = GtkSource.LanguageManager.get_default().guess_language(
            str(self.path), None
        )
        if language is None:
            mapped = language_for_path(self.path)
            language = GtkSource.LanguageManager.get_default().get_language(
                mapped.name.lower()
            ) if mapped else None
        self.buffer.set_language(language)
        self.buffer.set_highlight_syntax(language is not None)
