"""NO SHELL INTERPOLATION — argv-list enforcement for every subprocess."""
from __future__ import annotations

from aether_core.errors import IpcError

FORBIDDEN_CHARS = set(";|&$`\n\r<>")


def assert_argv_safe(argv: list[str]) -> list[str]:
    """All subprocess usage MUST pass through this check."""
    for arg in argv:
        if not isinstance(arg, str):
            raise IpcError("E_SAFETY", "argv items must be strings")
        if any(c in arg for c in FORBIDDEN_CHARS):
            raise IpcError("E_SAFETY", f"forbidden character in argv item: {arg[:40]!r}")
    return argv
