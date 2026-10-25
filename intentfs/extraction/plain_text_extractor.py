"""Plain text extractor (utf-8 with replace)."""
from __future__ import annotations

from pathlib import Path


class PlainTextExtractor:
    def name(self) -> str:
        return "plain-text@1"

    def extract(self, path: Path) -> dict:
        try:
            text = path.read_text(errors="replace")
            return {"ok": True, "text": text[:200000]}
        except OSError as e:
            return {"ok": False, "reason": str(e)}
