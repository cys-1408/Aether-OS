"""Status dashboard text (truthful)."""
from __future__ import annotations


def status_text(app) -> str:
    data = app.services.call("backup", "Backup.status", {})
    if not data:
        return "backup service unreachable — nothing is claimed about backup state"
    targets = data.get("targets", {})
    last = data.get("last_backup")
    if not last:
        return "No backup taken yet. Configure a target and run one — until then, restore will honestly report nothing available."
    return (f"last backup: {last} ({data.get('files', 0)} files, {data.get('bytes', 0):,} bytes)\n"
            f"verified: {data.get('verified', False)}\nconfigured targets: {targets.get('targets', [])}")
