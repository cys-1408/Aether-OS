"""Office extraction (docx/pptx/xlsx) via stdlib zipfile+xml — real implementation."""
from __future__ import annotations

import re
import zipfile
from pathlib import Path

from xml.etree import ElementTree as ET


class OfficeExtractor:
    def name(self) -> str:
        return "office-zipxml@1"

    def extract(self, path: Path) -> dict:
        suffix = path.suffix.lower()
        try:
            with zipfile.ZipFile(path) as zf:
                if suffix == ".docx":
                    return {"ok": True, "text": self._docx(zf)[:200000]}
                if suffix == ".pptx":
                    return {"ok": True, "text": self._pptx(zf)[:200000]}
                if suffix == ".xlsx":
                    return {"ok": True, "text": self._xlsx(zf)[:200000]}
                return {"ok": False, "reason": f"unsupported office format {suffix}"}
        except (zipfile.BadZipFile, ET.ParseError, OSError) as e:
            return {"ok": False, "reason": str(e)}

    @staticmethod
    def _docx(zf) -> str:
        xml = zf.read("word/document.xml")
        text = re.sub(rb"<w:p[ >]", b"\n<w:p > ", xml)
        root = ET.fromstring(text)
        return " ".join(t.text or "" for t in root.iter() if t.tag.endswith("}t"))

    @staticmethod
    def _pptx(zf) -> str:
        parts = []
        for name in sorted(zf.namelist()):
            if re.match(r"ppt/slides/slide\d+\.xml", name):
                root = ET.fromstring(zf.read(name))
                parts.append(" ".join(t.text or "" for t in root.iter() if t.tag.endswith("}t")))
        return " ".join(parts)

    @staticmethod
    def _xlsx(zf) -> str:
        root = ET.fromstring(zf.read("xl/sharedStrings.xml"))
        return " ".join("".join(t.text or "" for t in si.iter() if t.tag.endswith("}t"))
                        for si in root if si.tag.endswith("}si"))
