"""Find & replace bar: literal or regex, case toggle, real replace-all counts."""

from __future__ import annotations

import re

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

FIND_TAG_NAME = "find-match"


class FindReplaceBar(Gtk.Box):
    """Embedded search bar for the code editor."""

    def __init__(self, editor_view, get_buffer) -> None:
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=4, margin=6)
        self._view = editor_view
        self._get_buffer = get_buffer
        self._tag_added = False

        row1 = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        self.find_entry = Gtk.SearchEntry()
        self.find_entry.set_placeholder_text("Find")
        self.find_entry.connect("activate", lambda _e: self.find_next())
        self.find_entry.connect("search-changed", lambda _e: self.find_all())
        self.case_check = Gtk.CheckButton(label="Match case")
        self.count_label = Gtk.Label(label="", xalign=0)
        self.count_label.get_style_context().add_class("aether-muted")
        close_btn = Gtk.Button(label="×")
        close_btn.set_relief(Gtk.ReliefStyle.NONE)
        close_btn.connect("clicked", lambda _b: self.hide())
        row1.pack_start(self.find_entry, True, True, 0)
        row1.pack_start(self.case_check, False, False, 0)
        row1.pack_start(self.count_label, False, False, 0)
        row1.pack_end(close_btn, False, False, 0)

        row2 = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        self.replace_entry = Gtk.Entry()
        self.replace_entry.set_placeholder_text("Replace with")
        replace_btn = Gtk.Button(label="Replace")
        replace_btn.get_style_context().add_class("btn-soft")
        replace_btn.connect("clicked", lambda _b: self.replace_current())
        replace_all_btn = Gtk.Button(label="Replace all")
        replace_all_btn.get_style_context().add_class("btn-soft")
        replace_all_btn.connect("clicked", lambda _b: self.replace_all())
        self.regex_check = Gtk.CheckButton(label="Regex")
        row2.pack_start(self.replace_entry, True, True, 0)
        row2.pack_start(self.regex_check, False, False, 0)
        row2.pack_start(replace_btn, False, False, 0)
        row2.pack_start(replace_all_btn, False, False, 0)

        self.pack_start(row1, False, False, 0)
        self.pack_start(row2, False, False, 0)
        self.set_no_show_all(True)
        self.hide()

    # -- matching ------------------------------------------------------------------

    def _matches(self, text: str):
        needle = self.find_entry.get_text()
        if not needle:
            return []
        flags = 0 if self.case_check.get_active() else re.IGNORECASE
        if self.regex_check.get_active():
            try:
                pattern = re.compile(needle, flags)
            except re.error as exc:
                self.count_label.set_text(f"Invalid regex: {exc}")
                return []
            return [m.span() for m in pattern.finditer(text)]
        spans = []
        start = 0
        lowered = text.lower() if not self.case_check.get_active() else text
        target = needle.lower() if not self.case_check.get_active() else needle
        while True:
            index = lowered.find(target, start)
            if index == -1:
                break
            spans.append((index, index + len(needle)))
            start = index + max(len(needle), 1)
        return spans

    def _text_and_iter(self, offset: int):
        buffer = self._get_buffer()
        start, _end = buffer.get_bounds()
        text = buffer.get_text(start, _end, True)
        target = buffer.get_iter_at_offset(min(offset, buffer.get_char_count()))
        return text, target

    def _ensure_tag(self, buffer):
        table = buffer.get_tag_table()
        tag = table.lookup(FIND_TAG_NAME)
        if tag is None:
            tag = buffer.create_tag(FIND_TAG_NAME, background="#ffbd2e")
        return tag

    # -- actions --------------------------------------------------------------------

    def find_all(self) -> int:
        buffer = self._get_buffer()
        start, end = buffer.get_bounds()
        buffer.remove_tag(self._ensure_tag(buffer), start, end)
        text = buffer.get_text(start, end, True)
        spans = self._matches(text)
        tag = self._ensure_tag(buffer)
        for begin, finish in spans[:2000]:
            buffer.apply_tag(tag, buffer.get_iter_at_offset(begin),
                             buffer.get_iter_at_offset(finish))
        self.count_label.set_text(f"{len(spans)} match(es)" if spans else "No matches")
        return len(spans)

    def find_next(self) -> bool:
        buffer = self._get_buffer()
        mark = buffer.get_insert()
        current = buffer.get_iter_at_mark(mark).get_offset()
        text, _ = self._text_and_iter(0)
        spans = self._matches(text)
        if not spans:
            self.find_all()
            return False
        for begin, finish in spans:
            if begin >= current:
                self._select(begin, finish)
                return True
        begin, finish = spans[0]  # wrap around
        self._select(begin, finish)
        return True

    def _select(self, begin: int, finish: int) -> None:
        buffer = self._get_buffer()
        start_iter = buffer.get_iter_at_offset(begin)
        end_iter = buffer.get_iter_at_offset(finish)
        buffer.select_range(start_iter, end_iter)
        self._view.scroll_to_iter(start_iter, 0.1, True, 0.0, 0.4)

    def replace_current(self) -> None:
        buffer = self._get_buffer()
        bounds = buffer.get_selection_bounds()
        if not bounds:
            self.find_next()
            return
        start, end = bounds
        selected = buffer.get_text(start, end, True)
        if self._is_match(selected):
            buffer.delete(start, end)
            buffer.insert_at_cursor(self._expand_replacement(selected))
        self.find_next()

    def replace_all(self) -> int:
        buffer = self._get_buffer()
        start, end = buffer.get_bounds()
        text = buffer.get_text(start, end, True)
        spans = self._matches(text)
        if not spans:
            self.count_label.set_text("No matches")
            return 0
        result = []
        last = 0
        replacement = self.replace_entry.get_text()
        for begin, finish in spans:
            matched = text[begin:finish]
            result.append(text[last:begin])
            result.append(self._expand_replacement(matched, replacement))
            last = finish
        result.append(text[last:])
        buffer.set_text("".join(result))
        self.find_all()
        return len(spans)

    def _is_match(self, candidate: str) -> bool:
        spans = self._matches(candidate)
        return any(begin == 0 and finish == len(candidate) for begin, finish in spans)

    def _expand_replacement(self, matched: str, replacement: str | None = None) -> str:
        replacement = self.replace_entry.get_text() if replacement is None else replacement
        if self.regex_check.get_active():
            try:
                return re.sub(self.find_entry.get_text(), replacement, matched, count=1)
            except re.error:
                return replacement
        return replacement
