"""Rollback trigger: restore the known-good state when health policy demands."""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from apply.post_update_health import ROLLOVER_FAILURES  # noqa: E402
from rollback import rollback  # noqa: E402


def should_rollback(health: dict) -> bool:
    """Failure policy: any ROLLOVER-failure-limited check that failed."""
    return any(f in ROLLOVER_FAILURES for f in health.get("checks_failed", []))


def trigger(health: dict) -> dict:
    if not health.get("rollback_required") or not should_rollback(health):
        return {"triggered": False, "reason": "health policy not breached"}
    result = rollback()
    return {"triggered": True, "health": {"failed": health.get("checks_failed")},
            "rollback": result}
