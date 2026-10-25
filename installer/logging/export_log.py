"""Export the installer log (redacted)."""
from __future__ import annotations

import shutil
from pathlib import Path

from logging.secret_filter import scrub  # type: ignore  # local module
from aether_core import paths


def export(destination: str) -> str:
    src = paths.SYSTEM_STATE_DIR / "installer" / "install.log"
    if not src.exists():
        return "no installer log yet"
    text = scrub(src.read_text())
    dst = Path(destination).expanduser()
    dst.write_text(text)
    return str(dst)
