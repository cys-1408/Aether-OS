"""Hard sensitive-path policy (never indexed regardless of user config)."""
from __future__ import annotations

from pathlib import Path

HARD_DENY = ("~/.ssh", "~/.gnupg", "~/.config/aether/secrets", "/etc/shadow")


def denied(path: str) -> bool:
    p = str(Path(path).expanduser())
    return any(p.startswith(str(Path(d).expanduser())) for d in HARD_DENY)
