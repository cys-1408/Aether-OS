"""Writer document model: title, content, dirty flag, timestamps."""

from __future__ import annotations

import datetime
import hashlib
from pathlib import Path

SUPPORTED_EXTENSIONS = (".md", ".markdown", ".txt")


class Document:
    """In-memory document with real change tracking."""

    def __init__(self, title: str = "Untitled", content: str = "",
                 path: Path | None = None) -> None:
        self.title = title
        self.content = content
        self.path = Path(path) if path else None
        now = datetime.datetime.now().isoformat(timespec="seconds")
        self.created = now
        self.modified = now
        self._saved_content = content

    # -- state -----------------------------------------------------------------

    @property
    def dirty(self) -> bool:
        return self.content != self._saved_content

    def mark_saved(self) -> None:
        self._saved_content = self.content

    def touch(self) -> None:
        self.modified = datetime.datetime.now().isoformat(timespec="seconds")

    @property
    def display_name(self) -> str:
        if self.path is not None:
            return self.path.name
        return self.title or "Untitled"

    @property
    def doc_id(self) -> str:
        """Stable id used for draft files (path-based, else title hash)."""
        if self.path is not None:
            digest = hashlib.sha256(str(self.path.resolve()).encode()).hexdigest()[:16]
            return f"{self.path.stem}-{digest}"
        digest = hashlib.sha256(self.title.encode()).hexdigest()[:16]
        return f"untitled-{digest}"

    # -- metrics -----------------------------------------------------------------

    @property
    def word_count(self) -> int:
        return len(self.content.split())

    @property
    def char_count(self) -> int:
        return len(self.content)

    def summary_line(self) -> str:
        suffix = " •" if self.dirty else ""
        return f"{self.display_name} — {self.word_count} words, {self.char_count} chars{suffix}"
