"""Working-directory tracking via OSC 7 sequences emitted by modern shells.

Shells that set ``PROMPT_COMMAND``/precmd to emit OSC 7
(``ESC ] 7 ; file://host/path BEL``) report their cwd on every prompt. The
tracker scans raw PTY output for these sequences and also understands the
ST terminator (``ESC \\``). Vte exposes the same information through its
``current-directory-uri`` property, which the VTE path feeds into the tracker.
"""

from __future__ import annotations

import os
from pathlib import Path
from urllib.parse import unquote, urlparse

OSC7_PREFIX = b"\x1b]7;"


class WorkingDirectoryTracker:
    """Extracts the shell cwd from the terminal output stream."""

    def __init__(self, initial_cwd: str | None = None) -> None:
        self.current = Path(initial_cwd or Path.home())
        self._buffer = b""

    def feed(self, data: bytes) -> Path | None:
        """Consume PTY output; returns the new cwd when OSC 7 reports one."""
        self._buffer += data
        updated = None
        while True:
            start = self._buffer.find(OSC7_PREFIX)
            if start == -1:
                # keep a small tail in case a sequence spans chunk boundaries
                self._buffer = self._buffer[-(len(OSC7_PREFIX) + 512):]
                break
            rest = self._buffer[start + len(OSC7_PREFIX):]
            end_bell = rest.find(b"\x07")
            end_st = rest.find(b"\x1b\\")
            ends = [pos for pos in (end_bell, end_st) if pos != -1]
            if not ends:
                if len(rest) > 4096:  # malformed, drop it
                    self._buffer = b""
                else:
                    self._buffer = self._buffer[start:]
                break
            end = min(ends)
            uri = rest[:end].decode("utf-8", errors="replace")
            cwd = self._parse_uri(uri)
            if cwd:
                self.current = cwd
                updated = cwd
            self._buffer = rest[end + (1 if end == end_bell else 2):]
        return updated

    @staticmethod
    def _parse_uri(uri: str) -> Path | None:
        uri = uri.strip()
        if not uri.startswith("file:"):
            return None
        parsed = urlparse(uri)
        path = unquote(parsed.path)
        if path and os.path.isdir(path):
            return Path(path)
        return None

    def prompt_text(self) -> str:
        """Short path for the prompt row: ~-relative when inside home."""
        try:
            return "~" + str(self.current)[len(str(Path.home())):]
        except ValueError:
            return str(self.current)
