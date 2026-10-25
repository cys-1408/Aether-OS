"""Discover installed backends (llama-server on PATH or /usr/lib/aether/backends)."""
from __future__ import annotations

import shutil


def discover() -> list[str]:
    found = []
    for name in ("llama-server",):
        if shutil.which(name):
            found.append(shutil.which(name))
    for candidate in ("/usr/lib/aether/backends/llama-server",):
        try:
            if Path := __import__("pathlib").Path:
                p = __import__("pathlib").Path(candidate)
                if p.exists() and p.stat().st_mode & 0o111:
                    found.append(candidate)
        except OSError:
            continue
    return found
