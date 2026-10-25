"""Capability open_app — launch an application through the Shell."""

from __future__ import annotations

from aether_core.errors import AetherError

from miso.capabilities.apps import SHELL_METHODS
from miso.capabilities._shell import shell_call

KNOWN_APP_IDS = {
    "org.aether.Apps.Files": "files",
    "org.aether.Apps.Writer": "writer",
    "org.aether.Apps.Terminal": "terminal",
    "org.aether.Apps.Code": "code",
    "org.aether.Apps.Clock": "clock",
    "org.aether.Apps.Focus": "focus",
    "org.aether.Apps.Calculator": "calculator",
    "org.aether.Apps.Gallery": "gallery",
    "org.aether.Apps.SystemMonitor": "system monitor",
    "org.aether.Apps.Settings": "settings",
    "org.aether.Apps.SoftwareCenter": "software center",
    "org.aether.Apps.Screenshot": "screenshot",
    "org.aether.Apps.ArchiveManager": "archive manager",
    "org.aether.Apps.BackupCenter": "backup center",
    "org.aether.Apps.RecoveryCenter": "recovery center",
    "org.aether.Apps.Mines": "mines",
}


def normalize_app_id(name: str) -> str:
    """Map a human app name or partial id to a plausible app_id slug."""
    lowered = name.strip().lower()
    for app_id, label in KNOWN_APP_IDS.items():
        if lowered == label or lowered == app_id.lower() or lowered in app_id.lower():
            return app_id
    slug = lowered.replace(" ", "-")
    if "." not in slug:
        return f"org.aether.Apps.{slug.title().replace('-', '')}"
    return slug


def execute(params: dict, ctx: dict) -> dict:
    """Open an app by id or human name; returns the id actually requested."""
    app_id = str(params.get("app_id", "")).strip()
    if not app_id:
        raise AetherError("missing_param", "open_app requires app_id")
    if " " in app_id and "." not in app_id:
        app_id = normalize_app_id(app_id)
    args = params.get("args") or []
    if not isinstance(args, list) or any(not isinstance(a, str) for a in args):
        raise AetherError("invalid_params", "args must be a list of strings")
    result = shell_call(ctx["uid"], SHELL_METHODS["open_app"],
                        {"app_id": app_id, "args": args})
    return {
        "app_id": app_id,
        "launched": bool(result.get("launched", True)),
        "detail": {k: v for k, v in result.items() if k not in ("launched",)},
    }
