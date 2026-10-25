"""Optional OCR via tesseract — honest absence."""
from __future__ import annotations

import shutil
import subprocess


def ocr(image_path, timeout: int = 60) -> dict:
    if not shutil.which("tesseract"):
        return {"supported": False, "reason": "tesseract not installed (optional package)"}
    try:
        out = subprocess.run(["tesseract", str(image_path), "-", "--psm", "3"],
                             capture_output=True, text=True, timeout=timeout)
        return {"supported": True, "text": out.stdout[:10000]}
    except subprocess.TimeoutExpired:
        return {"supported": False, "reason": "ocr timed out"}
