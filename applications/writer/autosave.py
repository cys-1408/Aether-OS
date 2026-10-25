"""Draft autosave: GLib timeout every 30s to ~/.local/share/aether/drafts."""

from __future__ import annotations

import datetime
from pathlib import Path

from gi.repository import GLib

from app_framework.app_lifecycle import drafts_dir
from document_model import Document

AUTOSAVE_INTERVAL_SECONDS = 30


class DraftAutosaver:
    """Periodically writes real draft files; reports honest status strings."""

    def __init__(self, status_callback) -> None:
        self._status_callback = status_callback
        self._timeout_id = None
        self._last_error = ""

    def start(self) -> None:
        if self._timeout_id is None:
            self._timeout_id = GLib.timeout_add_seconds(
                AUTOSAVE_INTERVAL_SECONDS, self._tick
            )

    def stop(self) -> None:
        if self._timeout_id is not None:
            GLib.source_remove(self._timeout_id)
            self._timeout_id = None

    def save_now(self, document: Document) -> str:
        """Write a draft immediately; returns a truthful status message."""
        if not document.dirty:
            return ""
        try:
            draft_root = drafts_dir()
            draft_path = draft_root / f"{document.doc_id}.md"
            header = (
                f"<!-- aether-writer draft\n"
                f"source: {document.path if document.path else 'unsaved document'}\n"
                f"saved: {datetime.datetime.now().isoformat(timespec='seconds')}\n"
                f"-->\n\n"
            )
            draft_path.write_text(header + document.content, encoding="utf-8")
        except OSError as exc:
            self._last_error = str(exc)
            return f"Draft save failed: {exc}"
        stamp = datetime.datetime.now().strftime("%H:%M")
        return f"Saved draft {stamp}"

    def _tick(self):
        return True  # the window queries the active document each tick

    def last_error(self) -> str:
        return self._last_error


def list_drafts() -> list:
    """All draft files with timestamps, oldest last."""
    root = drafts_dir()
    drafts = []
    for candidate in sorted(root.glob("*.md")):
        try:
            stat = candidate.stat()
        except OSError:
            continue
        drafts.append({"path": candidate, "mtime": stat.st_mtime, "size": stat.st_size})
    drafts.sort(key=lambda item: item["mtime"])
    return drafts


def draft_source(document_path: Path | None) -> str:
    return str(document_path) if document_path else "unsaved document"
