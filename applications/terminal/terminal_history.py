"""Terminal scrollback buffer with real search and copy support."""

from __future__ import annotations

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

MAX_SCROLLBACK_LINES = 5000


class TerminalHistory:
    """Backs the fallback TextView terminal: append, trim, search, highlight."""

    def __init__(self, textview: Gtk.TextView) -> None:
        self.view = textview
        self.buffer = textview.get_buffer()
        self._mark_end = self.buffer.create_mark("append-end", self.buffer.get_end_iter())
        self._search_tag = self.buffer.create_tag("search-hit", background="#8fa9c4")
        self._current_hits = []
        self._hit_index = 0
        self._search_term = ""

    def append(self, text: str) -> None:
        self.buffer.insert(self.buffer.get_end_iter(), text)
        self._trim()
        self.view.scroll_mark_onscreen(self.buffer.get_insert())

    def append_chunk(self, data: bytes) -> None:
        text = data.decode("utf-8", errors="replace")
        # Strip escape sequences the plain renderer cannot interpret (keep text).
        text = _strip_ansi(text)
        if text:
            self.append(text)

    def _trim(self) -> None:
        line_count = self.buffer.get_line_count()
        if line_count > MAX_SCROLLBACK_LINES:
            start = self.buffer.get_iter_at_line(0)
            excess = self.buffer.get_iter_at_line(line_count - MAX_SCROLLBACK_LINES)
            self.buffer.delete(start, excess)

    def text(self) -> str:
        start, end = self.buffer.get_bounds()
        return self.buffer.get_text(start, end, True)

    # -- search ---------------------------------------------------------------

    def search(self, term: str) -> int:
        """Highlight every occurrence; returns the hit count."""
        self.clear_search()
        self._search_term = term
        if not term:
            return 0
        count = 0
        start = self.buffer.get_start_iter()
        while True:
            hit = start.forward_search(term, Gtk.TextSearchFlags.CASE_INSENSITIVE)
            if hit is None:
                break
            hit_start, hit_end = hit
            self.buffer.apply_tag(self._search_tag, hit_start, hit_end)
            self._current_hits.append((hit_start.get_offset(), hit_end.get_offset()))
            count += 1
            start = hit_end
        return count

    def clear_search(self) -> None:
        start, end = self.buffer.get_bounds()
        self.buffer.remove_tag(self._search_tag, start, end)
        self._current_hits = []
        self._hit_index = 0

    def jump_next_hit(self) -> bool:
        if not self._current_hits:
            return False
        self._hit_index = (self._hit_index + 1) % len(self._current_hits)
        offset, _end = self._current_hits[self._hit_index]
        target = self.buffer.get_iter_at_offset(offset)
        self.buffer.place_cursor(target)
        self.view.scroll_to_iter(target, 0.1, True, 0.0, 0.4)
        return True


_ANSI_SEQUENCES = (
    "\x1b[?25l", "\x1b[?25h", "\x1b[2J", "\x1b[H", "\x1b[K", "\x1b[0K",
    "\x1b[0G", "\x1b[?1049h", "\x1b[?1049l", "\x1b[?2004h", "\x1b[?2004l",
)


def _strip_ansi(text: str) -> str:
    """Remove ANSI control sequences the plain renderer cannot display."""
    import re

    csi = re.compile(r"\x1b\[[0-9;?]*[A-Za-z]")
    osc = re.compile(r"\x1b\][^\x07\x1b]*(\x07|\x1b\\)")
    simple = re.compile(r"\x1b[=>NOMc78]")
    text = osc.sub("", text)
    text = csi.sub("", text)
    text = simple.sub("", text)
    for seq in _ANSI_SEQUENCES:
        text = text.replace(seq, "")
    return text.replace("\r\n", "\n").replace("\r", "")
