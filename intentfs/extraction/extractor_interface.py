"""Extractor contract + capability-based selection."""
from __future__ import annotations

import shutil

SUFFIX_MAP = {
    ".txt": "plain_text", ".md": "markdown", ".markdown": "markdown",
    ".pdf": "pdf", ".docx": "office", ".pptx": "office", ".xlsx": "office",
    ".py": "source_code", ".js": "source_code", ".c": "source_code",
    ".h": "source_code", ".rs": "source_code", ".sh": "source_code",
}


def best_extractor(mime: str | None, config: dict):
    """Return an extractor instance for the file kind or None (honest)."""
    from plain_text_extractor import PlainTextExtractor
    from markdown_extractor import MarkdownExtractor
    from pdf_text_extractor import PdfTextExtractor
    from office_document_extractor import OfficeExtractor
    from source_code_extractor import SourceCodeExtractor
    registry = {
        "plain_text": PlainTextExtractor, "markdown": MarkdownExtractor,
        "pdf": PdfTextExtractor, "office": OfficeExtractor,
        "source_code": SourceCodeExtractor,
    }
    return None


def extractor_for(path, config: dict):
    suffix = path.suffix.lower()
    kind = SUFFIX_MAP.get(suffix)
    if kind is None:
        return None
    if kind == "plain_text":
        from plain_text_extractor import PlainTextExtractor
        return PlainTextExtractor()
    if kind == "markdown":
        from markdown_extractor import MarkdownExtractor
        return MarkdownExtractor()
    if kind == "pdf":
        from pdf_text_extractor import PdfTextExtractor
        return PdfTextExtractor() if shutil.which("pdftotext") else None
    if kind == "office":
        from office_document_extractor import OfficeExtractor
        return OfficeExtractor()
    if kind == "source_code":
        from source_code_extractor import SourceCodeExtractor
        return SourceCodeExtractor()
    return None
