"""Canonical Aether paths."""
from __future__ import annotations

import os
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
SYSTEM_RUNTIME_DIR = Path("/run/aether")
SYSTEM_STATE_DIR = Path("/var/lib/aether")
SYSTEM_CONFIG_DIR = Path("/etc/aether")
USER_CONFIG_DIR = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config")) / "aether"
USER_STATE_DIR = Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local/share")) / "aether"
USER_CACHE_DIR = Path(os.environ.get("XDG_CACHE_HOME", Path.home() / ".cache")) / "aether"
USER_RUNTIME_DIR = Path(os.environ.get("XDG_RUNTIME_DIR", f"/run/user/{os.getuid()}")) / "aether"


def system_socket(name: str) -> Path:
    return SYSTEM_RUNTIME_DIR / f"{name}.sock"


def user_socket(name: str) -> Path:
    return USER_RUNTIME_DIR / f"{name}.sock"


def resolve_socket(name: str) -> Path:
    """Resolve a CONVENTIONS §4 socket name against the right scope."""
    if name in ("shell", "agent", "trash", "clipboard", "reminders"):
        return user_socket(name)
    return system_socket(name)


def ensure_user_dirs() -> None:
    for d in (USER_CONFIG_DIR, USER_STATE_DIR, USER_CACHE_DIR, USER_RUNTIME_DIR):
        d.mkdir(parents=True, exist_ok=True)


def redact_note() -> str:
    return "logs are redacted via system/logging/redaction-rules.yaml"
