"""MIME detection: file(1) when available, extension fallback."""
from __future__ import annotations

import subprocess
from pathlib import Path

EXT_MAP = {".txt": "text/plain", ".md": "text/markdown", ".pdf": "application/pdf",
           ".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg",
           ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
           ".pptx": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
           ".xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
           ".py": "text/x-python", ".js": "text/javascript", ".c": "text/x-csrc",
           ".h": "text/x-chdr", ".sh": "text/x-shellscript", ".rs": "text/x-rust",
           ".zip": "application/zip", ".html": "text/html", ".json": "application/json"}


def mime_type_of(path: Path) -> str | None:
    try:
        out = subprocess.run(["file", "--mime-type", "-b", str(path)],
                             capture_output=True, text=True, timeout=5)
        if out.returncode == 0 and "/" in out.stdout:
            return out.stdout.strip()
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass
    return EXT_MAP.get(path.suffix.lower())
