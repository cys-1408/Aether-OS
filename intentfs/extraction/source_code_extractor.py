"""Source code extractor: text + comment-stripped view."""
from __future__ import annotations

import re
from pathlib import Path


class SourceCodeExtractor:
    def name(self) -> str:
        return "source-code@1"

    def extract(self, path: Path) -> dict:
        try:
            text = path.read_text(errors="replace")
        except OSError as e:
            return {"ok": False, "reason": str(e)}
        no_comments = re.sub(r"#[^\n]*|//[^\n]*|/\*.*?\*/", " ", text, flags=re.S)
        return {"ok": True, "text": no_comments[:200000]}
