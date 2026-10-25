"""Update planning: space estimate, compatibility checks, reboot decision."""
from __future__ import annotations

import shutil
import subprocess

from update_checker import check  # type: ignore


def _du_needed(updates: list) -> int:
    """Sum of download+install size from pacman's print-format %S line, else 0."""
    try:
        out = subprocess.run(["pacman", "-Sup", "--print-format", "%n %S"],
                             capture_output=True, text=True, timeout=300)
        total = 0
        for line in out.stdout.splitlines():
            parts = line.split()
            if len(parts) == 2 and parts[1].isdigit():
                total += int(parts[1])
        return total
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return 0


def plan() -> dict:
    updates = check()
    pkg_list = updates.get("updates", [])
    needed = _du_needed(pkg_list)
    free = shutil.disk_usage("/").free if updates.get("status") == "updates-available" else None
    plan_out = {
        "status": updates.get("status"),
        "summary": updates.get("summary"),
        "space_needed_bytes": needed,
        "free_bytes": free,
        "space_ok": (free is None) or (free > needed * 2),
        "compatibility": {
            "kernel": any(n == "linux-aether" for n, *_ in pkg_list),
            "reboot_required": any(n.startswith("linux-aether") for n, *_ in pkg_list),
        },
        "steps": ["verify metadata", "verify digests", "stage (download-only)",
                  "confirm with user", "apply", "post-update health",
                  "rollback on failed health"],
    }
    if pkg_list and not plan_out["space_ok"]:
        plan_out["blocked"] = "insufficient free space for a safe update"
    return plan_out
