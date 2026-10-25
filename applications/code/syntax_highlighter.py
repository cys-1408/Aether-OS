"""Syntax highlighting: GtkSourceView preferred, regex tagger as fallback.

The fallback tagger is real code: per-line keyword/string/comment/number
scanning with compiled regular expressions and Gtk.TextTag styling, debounced
on buffer changes.
"""

from __future__ import annotations

import re

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import GLib, Gtk

from editor_buffer import GTKSOURCE_AVAILABLE, EditorBuffer
from language_support import HighlightPalette, language_for_path


def make_editor_view(buffer: EditorBuffer):
    """Return the best available editor widget for the buffer."""
    if GTKSOURCE_AVAILABLE and buffer.is_gtksource:
        view = GtkSource.View()
        view.set_show_line_numbers(True)
        view.set_highlight_current_line(True)
        view.set_indent_width(4)
        view.set_insert_spaces_instead_of_tabs(True)
        view.set_auto_indent(True)
        return view
    view = Gtk.TextView()
    view.set_monospace(True)
    view.set_wrap_mode(Gtk.WrapMode.NONE)
    view.set_left_margin(8)
    return view


class RegexHighlighter:
    """Fallback highlighter applying tags over the whole buffer."""

    DEBOUNCE_MS = 180

    def __init__(self, buffer: EditorBuffer, path) -> None:
        self._buffer = buffer.buffer
        self._language = language_for_path(path)
        self._palette = HighlightPalette()
        self._tags = {}
        self._pending_id = 0
        self._build_tags()
        self._build_patterns()
        buffer.buffer.connect("changed", self._on_changed)

    def _build_tags(self):
        for name, color, style in (
            ("keyword", self._palette.keyword, "bold"),
            ("string", self._palette.string, "normal"),
            ("comment", self._palette.comment, "italic"),
            ("number", self._palette.number, "normal"),
            ("heading", self._palette.heading, "bold"),
        ):
            tag = self._buffer.create_tag(f"hl-{name}", foreground=color)
            if style == "bold":
                tag.set_property("weight", 700)
            elif style == "italic":
                tag.set_property("style", 2)  # Pango.Style.ITALIC
            self._tags[name] = tag

    def _build_patterns(self):
        words = "|".join(
            re.escape(word) for word in self._language.keywords
        ) if self._language.keywords else ""
        self._keyword_re = re.compile(rf"\b({words})\b") if words else None
        self._number_re = re.compile(r"\b(0x[0-9a-fA-F]+|\d+(\.\d+)?)\b")
        string_chars = "".join(re.escape(c) for c in self._language.strings)
        self._string_re = (
            re.compile(rf"({string_chars})(?:\\.|[^\\])*?\1")
            if string_chars else None
        )
        comment_tokens = [re.escape(tok) for tok in self._language.line_comments]
        self._comment_re = (
            re.compile(rf"({'|'.join(comment_tokens)}).*") if comment_tokens else None
        )

    def _on_changed(self, _buffer):
        if self._pending_id:
            GLib.source_remove(self._pending_id)
        self._pending_id = GLib.timeout_add(self.DEBOUNCE_MS, self._apply_all)

    def _apply_all(self):
        self._pending_id = 0
        start, end = self._buffer.get_bounds()
        self._buffer.remove_all_tags(start, end)
        line_iter = self._buffer.get_start_iter()
        while True:
            line_start = line_iter.copy()
            line_end = line_iter.copy()
            if not line_end.forward_to_line_end():
                line_end = self._buffer.get_end_iter()
            text = self._buffer.get_text(line_start, line_end, True)
            self._highlight_line(line_start, text)
            if not line_iter.forward_line():
                break
        return GLib.SOURCE_REMOVE

    def _highlight_line(self, line_start, text: str) -> None:
        stripped = text.lstrip()

        if self._language.name == "Markdown":
            if stripped.startswith("#"):
                self._apply(line_start, 0, len(text), "heading")
            if stripped.startswith("```"):
                self._apply(line_start, 0, len(text), "comment")
            return

        comment_match = self._comment_re.search(text) if self._comment_re else None
        code_end = comment_match.start() if comment_match else len(text)

        if self._string_re is not None:
            for match in self._string_re.finditer(text, 0, code_end):
                self._apply(line_start, match.start(), match.end() - match.start(), "string")
        if self._keyword_re is not None:
            for match in self._keyword_re.finditer(text, 0, code_end):
                self._apply(line_start, match.start(), match.end() - match.start(), "keyword")
        for match in self._number_re.finditer(text, 0, code_end):
            self._apply(line_start, match.start(), match.end() - match.start(), "number")
        if comment_match:
            self._apply(line_start, comment_match.start(),
                        len(text) - comment_match.start(), "comment")

    def _apply(self, line_start, offset: int, length: int, tag_name: str) -> None:
        if length <= 0:
            return
        start = line_start.copy()
        start.forward_chars(offset)
        end = start.copy()
        end.forward_chars(length)
        self._buffer.apply_tag(self._tags[tag_name], start, end)


def attach_highlighting(buffer: EditorBuffer, path) -> str:
    """Wire highlighting for a buffer; returns the renderer description."""
    if GTKSOURCE_AVAILABLE and buffer.is_gtksource:
        return "GtkSourceView"
    RegexHighlighter(buffer, path)
    return "regex highlighter (GtkSourceView not available)"
