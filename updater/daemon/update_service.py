"""Update service: coordinate discovery -> verification -> plan -> stage -> apply.

Thin coordinator over the flat updater modules so both the systemd unit
(system/services/aether-update-check.service) and the CLI share one entry.
Every stage returns honest state; nothing reports success before the owning
operation confirms it.
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from update_checker import check  # noqa: E402
import metadata_verifier  # noqa: E402
from staging import stage  # noqa: E402
from apply import apply  # noqa: E402
from commit import commit  # noqa: E402


def status() -> dict:
    state = check()
    state["checked_at"] = time.strftime("%Y-%m-%dT%H:%M:%S%z")
    return state


def preflight() -> dict:
    checks = check()
    verified: dict | None = None
    repo_db = Path("/var/lib/pacman/sync/aether-repo.db")
    if repo_db.exists():
        verified = metadata_verifier.verify_repo(repo_db)
    return {"updates": checks, "repo_metadata": verified or {"verified": None,
            "reason": "no repo db present"}}


def apply_update(confirmed: bool) -> dict:
    """Full apply flow: stage (download-only) then confirmed activation."""
    pre = preflight()
    staged = stage()
    if not staged.get("staged"):
        return {"applied": False, "stage": staged, "preflight": pre,
                "reason": "staging failed; nothing was changed"}
    result = apply(confirmed=confirmed)
    if result.get("applied"):
        result["commit"] = commit()
    return {"applied": result.get("applied", False), "stage": staged,
            "result": result}


def run_daemon_once() -> dict:
    """Entry for the update-check service/timer: honest status, no side effects."""
    state = preflight()
    state["acts"] = {"staged": False, "applied": False,
                     "note": "daemon check only; staging/apply require user action"}
    return state
