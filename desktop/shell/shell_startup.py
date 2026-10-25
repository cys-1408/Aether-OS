"""Startup: restore approved settings, verify services, open surfaces."""
from __future__ import annotations

from shell_settings import settings
from aether_core.ipc import call
from aether_core.errors import IpcError
from aether_core import paths


def startup_checks() -> dict:
    """Probe core services truthfully for the top bar + activity panel."""
    checks = {}
    for name, method in (("health", "Health.services"), ("notifications", "Notify.list"),
                         ("runtime", "Runtime.status"), ("intentfs", "IntentFS.status")):
        try:
            call(paths.resolve_socket(name), method, {}, timeout=3)
            checks[name] = "reachable"
        except IpcError as e:
            checks[name] = f"unreachable: {e.message}"
    return checks


def apply_settings(shell) -> None:
    s = settings()
    if s.get_boolean("reduced-motion"):
        shell.miso.enable_reduced_motion()
    if not s.get_boolean("miso-enabled"):
        shell.miso.hide()
    if s.get_boolean("high-contrast"):
        from theme.widget_style import apply_high_contrast
        apply_high_contrast()
