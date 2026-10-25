"""First-boot pend state in the freshly installed target."""
from __future__ import annotations

import json
from pathlib import Path

PENDING_FILE = "var/lib/aether/firstboot-pending"
CONTEXT_FILE = "var/lib/aether/firstboot-context.json"


def prepare(root: str) -> dict:
    base = Path(root) / "var/lib/aether"
    base.mkdir(parents=True, exist_ok=True)
    (Path(root) / PENDING_FILE).write_text("1\n")
    return {"firstboot": "pending"}


def leave_firstboot_pending(root: str, *, username: str = "",
                            locale: str = "en_US.UTF-8",
                            timezone: str = "UTC", dry_run: bool = False) -> dict:
    """Persist the pending marker + install context the wizard resumes from."""
    if dry_run:
        return {"firstboot": "pending", "dry_run": True}
    base = Path(root) / "var/lib/aether"
    base.mkdir(parents=True, exist_ok=True)
    (Path(root) / PENDING_FILE).write_text("1\n")
    (Path(root) / CONTEXT_FILE).write_text(json.dumps({
        "version": 1,
        "username": username,
        "locale": locale,
        "timezone": timezone,
    }, indent=2))
    return {"firstboot": "pending", "username": username, "locale": locale,
            "timezone": timezone}
