"""Markdown extractor: strip md markers for cleaner concepts."""
from __future__ import annotations

import re
from pathlib import Path


class MarkdownExtractor:
    def name(self) -> str:
        return "markdown@1"

    def extract(self, path: Path) -> dict:
        try:
            text = path.read_text(errors="replace")
        except OSError as e:
            return {"ok": False, "reason": str(e)}
        text = re.sub(r"```.*?```", " ", text, flags=re.S)
        text = re.sub(r"`([^`]*)`", r"\1", text)
        text = re.sub(r"!\[.*?\]\(.*?\)", " ", text)
        text = re.sub(r"\[([^\]]*)\]\(.*?\)", r"\1", text)
        text = re.sub(r"^#{1,6}\s+", "", text, flags=re.M)
        text = re.sub(r"[*_~>#|-]{1,3}", " ", text)
        return {"ok": True, "text": re.sub(r"\s+", " ", text)[:200000]}
