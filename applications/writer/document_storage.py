"""Document persistence: open/save .md and .txt with atomic writes."""

from __future__ import annotations

from pathlib import Path

from app_framework.app_lifecycle import atomic_write_text
from document_model import Document, SUPPORTED_EXTENSIONS


class DocumentStorageError(RuntimeError):
    pass


def _detect_title(path: Path, content: str) -> str:
    for line in content.splitlines():
        stripped = line.strip()
        if stripped.startswith("# "):
            return stripped[2:].strip()[:80]
        if stripped:
            return stripped[:80]
    return path.stem


def open_document(path: Path) -> Document:
    path = Path(path).expanduser()
    if not path.is_file():
        raise DocumentStorageError(f"No such file: {path}")
    try:
        raw = path.read_bytes()
    except OSError as exc:
        raise DocumentStorageError(f"Cannot read {path}: {exc}") from exc
    try:
        content = raw.decode("utf-8")
        encoding = "utf-8"
    except UnicodeDecodeError as exc:
        raise DocumentStorageError(
            f"{path.name} is not valid UTF-8 text (byte {exc.start}); "
            "Writer opens plain text and markdown only."
        ) from exc
    return Document(
        title=_detect_title(path, content), content=content, path=path,
    )


def save_document(document: Document, path: Path | None = None) -> Path:
    """Write the document atomically; keeps the real extension contract."""
    target = Path(path) if path is not None else document.path
    if target is None:
        raise DocumentStorageError("No save target: use Save As to choose a file")
    if target.suffix.lower() not in SUPPORTED_EXTENSIONS:
        target = target.with_suffix(".md")
    try:
        atomic_write_text(target, document.content)
    except OSError as exc:
        raise DocumentStorageError(f"Save failed: {exc}") from exc
    document.path = target
    document.title = target.stem
    document.mark_saved()
    document.touch()
    return target
