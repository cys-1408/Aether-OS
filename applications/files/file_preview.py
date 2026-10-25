"""Inline preview: text, images, PDF first page — or an honest no-preview."""

from __future__ import annotations

from pathlib import Path

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import GdkPixbuf, GLib, Gtk

MAX_TEXT_BYTES = 4096
IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif", ".bmp", ".webp", ".svg", ".tiff", ".ico"}
PREVIEW_SIZE = 320


class FilePreview(Gtk.Box):
    """Renders what it truly can and says so when it cannot."""

    def __init__(self) -> None:
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=6, margin=8)
        self.set_size_request(260, -1)
        self._header = Gtk.Label(xalign=0)
        self._header.get_style_context().add_class("aether-title")
        self._body = Gtk.Label(xalign=0)
        self._body.set_line_wrap(True)
        self._body.set_selectable(True)
        self._image = Gtk.Image()
        self._text = Gtk.TextView()
        self._text.set_editable(False)
        self._text.set_cursor_visible(False)
        self._text.set_monospace(True)
        self._text.set_wrap_mode(Gtk.WrapMode.WORD_CHAR)
        self._text.set_size_request(-1, 220)
        text_scroll = Gtk.ScrolledWindow()
        text_scroll.set_size_request(-1, 220)
        text_scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        text_scroll.add(self._text)
        self.pack_start(self._header, False, False, 0)
        self.pack_start(self._image, False, False, 0)
        self.pack_start(text_scroll, True, True, 0)
        self.pack_start(self._body, False, False, 0)
        self.show_all()

    def show_file(self, path: Path) -> None:
        path = Path(path)
        for widget in (self._image, self._body, self._text.get_parent()):
            if widget is not None:
                widget.hide()
        self._header.set_text(path.name)
        if not path.is_file():
            self._set_message(f"No preview — {path.name} is not a regular file.")
            return
        suffix = path.suffix.lower()
        if suffix in IMAGE_EXTENSIONS:
            if self._show_image(path):
                return
        if suffix == ".pdf":
            if self._show_pdf_first_page(path):
                return
        if self._looks_like_text(path):
            self._show_text(path)
            return
        self._set_message("No preview available for this file type.")

    def clear(self, message: str = "Select a file to preview it here.") -> None:
        self._header.set_text("Preview")
        self._image.hide()
        text_parent = self._text.get_parent()
        if text_parent is not None:
            text_parent.hide()
        self._set_message(message)

    # -- helpers ---------------------------------------------------------------

    def _set_message(self, message: str) -> None:
        self._body.set_text(message)
        self._body.show()

    def _show_image(self, path: Path) -> bool:
        try:
            pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(
                str(path), PREVIEW_SIZE, PREVIEW_SIZE
            )
        except GLib.Error:
            self._set_message("No preview — image could not be decoded.")
            return False
        self._image.set_from_pixbuf(pixbuf)
        self._image.show()
        return True

    def _show_pdf_first_page(self, path: Path) -> bool:
        # GdkPixbuf can carry a PDF loader on some installs; try it first.
        try:
            pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(
                str(path), PREVIEW_SIZE, PREVIEW_SIZE
            )
            self._image.set_from_pixbuf(pixbuf)
            self._image.show()
            return True
        except GLib.Error:
            pass
        # Fall back to the gdk-pixbuf thumbnailer if it exists on this system.
        import shutil
        import subprocess

        thumbnailer = shutil.which("gdk-pixbuf-thumbnailer")
        if thumbnailer is None:
            self._set_message(
                "No preview — no PDF renderer available "
                "(gdk-pixbuf PDF loader or gdk-pixbuf-thumbnailer not installed)."
            )
            return False
        result = subprocess.run(
            [thumbnailer, str(path), "-s", str(PREVIEW_SIZE), "/dev/stdout"],
            capture_output=True, timeout=8,
        )
        if result.returncode != 0 or not result.stdout:
            self._set_message("No preview — the PDF thumbnailer failed for this file.")
            return False
        import io

        loader = GdkPixbuf.PixbufLoader()
        try:
            loader.write(result.stdout)
            loader.close()
        except GLib.Error:
            self._set_message("No preview — thumbnailer output could not be decoded.")
            return False
        self._image.set_from_pixbuf(loader.get_pixbuf())
        self._image.show()
        return True

    def _show_text(self, path: Path) -> None:
        try:
            raw = path.read_bytes()[:MAX_TEXT_BYTES]
            text = raw.decode("utf-8", errors="replace")
        except OSError as exc:
            self._set_message(f"No preview — read failed: {exc}")
            return
        text_parent = self._text.get_parent()
        if text_parent is not None:
            text_parent.show()
        self._text.get_buffer().set_text(text)
        suffix_note = "" if path.stat().st_size <= MAX_TEXT_BYTES else " (first 4 KB)"
        self._body.set_text(f"Text preview{suffix_note}")
        self._body.show()

    @staticmethod
    def _looks_like_text(path: Path) -> bool:
        try:
            chunk = path.open("rb").read(1024)
        except OSError:
            return False
        if not chunk:
            return True
        if b"\x00" in chunk:
            return False
        printable = sum(1 for b in chunk if 32 <= b < 127 or b in (9, 10, 13))
        return printable / len(chunk) > 0.7
