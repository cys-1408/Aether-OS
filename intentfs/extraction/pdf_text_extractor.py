"""PDF text layer via pdftotext (honest unsupported without poppler)."""
from __future__ import annotations

import subprocess
from pathlib import Path


class PdfTextExtractor:
    def name(self) -> str:
        return "pdftotext@1"

    def extract(self, path: Path) -> dict:
        try:
            out = subprocess.run(["pdftotext", "-l", "30", str(path), "-"],
                                 capture_output=True, text=True, timeout=30)
            if out.returncode != 0:
                return {"ok": False, "reason": out.stderr.strip()[:200]}
            return {"ok": True, "text": out.stdout[:200000]}
        except FileNotFoundError:
            return {"ok": False, "reason": "pdftotext not installed (install poppler)"}
        except subprocess.TimeoutExpired:
            return {"ok": False, "reason": "pdftotext timed out"}
