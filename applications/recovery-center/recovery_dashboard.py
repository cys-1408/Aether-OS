"""Recovery capability summary (honest)."""
from __future__ import annotations


def capabilities_text(app) -> str:
    lines = ["In-session recovery surfaces:"]
    runtime = app.services.call("runtime", "Runtime.status", {})
    lines.append(f"· AI runtime: {'reachable' if runtime else 'unreachable'}")
    intentfs = app.services.call("intentfs", "IntentFS.status", {})
    lines.append(f"· IntentFS: {'reachable' if intentfs else 'unreachable'}")
    lines.append("· update rollback: via updater journal + recovery boot entry")
    lines.append("· offline repairs (bootloader, initramfs, package db): recovery boot entry TUI")
    return "\n".join(lines)
