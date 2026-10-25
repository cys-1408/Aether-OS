"""Group membership via the polkit helper + real /etc/group reads."""
from __future__ import annotations

import subprocess
from pathlib import Path

HELPER = "/usr/libexec/aether/aether-account-helper"
MANAGED_GROUPS = ("wheel", "users", "aether-services")


def user_groups(username: str) -> list[str]:
    groups = []
    try:
        for line in Path("/etc/group").read_text().splitlines():
            parts = line.split(":")
            if len(parts) == 4 and username in parts[3].split(","):
                groups.append(parts[0])
    except OSError:
        pass
    return groups


def add_to_group(username: str, group: str) -> dict:
    if group not in MANAGED_GROUPS:
        return {"ok": False, "error": f"group {group!r} not managed by Aether"}
    proc = subprocess.run([HELPER, "add-group", username, group],
                          capture_output=True, text=True, timeout=30)
    return {"ok": proc.returncode == 0, "error": None if proc.returncode == 0 else proc.stderr.strip()}
