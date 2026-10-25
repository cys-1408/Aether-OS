"""Aggregated recovery status across boot, services, disks and updates."""

from __future__ import annotations

from .diagnostics.inspect_boot_state import boot_state
from .diagnostics.inspect_disk_state import disk_state
from .diagnostics.inspect_service_state import service_state
from .diagnostics.inspect_update_state import update_state


def recovery_status(*, chroot: str | None = None) -> dict:
    """Collect every status view; each one degrades honestly if tools miss."""
    status = {
        "boot": _safe(boot_state),
        "services": _safe(lambda: service_state(chroot=chroot)),
        "disks": _safe(disk_state),
        "updates": _safe(lambda: update_state(chroot=chroot)),
    }
    status["healthy"] = all(
        view.get("ok", False) for view in status.values() if isinstance(view, dict)
    )
    return status


def _safe(fn) -> dict:
    try:
        return fn()
    except Exception as exc:  # diagnostics must never crash the menu
        return {"ok": False, "error": f"{type(exc).__name__}: {exc}"}
