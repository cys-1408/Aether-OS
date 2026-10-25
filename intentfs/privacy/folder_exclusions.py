"""Exclusion matching (globs + sensitive paths)."""
from __future__ import annotations

import fnmatch
from pathlib import Path

SENSITIVE = ("~/.ssh", "~/.gnupg", "~/.config/aether/secrets")


def excluded(path: str, config: dict) -> bool:
    p = str(Path(path).expanduser())
    for pat in list(config.get("exclusions", [])) + SENSITIVE:
        pat_exp = str(Path(pat).expanduser())
        if p == pat_exp or p.startswith(pat_exp + "/"):
            return True
        if fnmatch.fnmatch(p, pat_exp):
            return True
    return False
