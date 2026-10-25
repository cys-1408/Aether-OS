"""Restore wizard flow (catalog → preview → confirm → restore)."""
from __future__ import annotations


def run_cli(mount: str, root: str) -> dict:
    from backup_catalog import scan
    from restore_preview import preview
    found = scan(mount)
    if not found:
        return {"restored": False, "reason": "no verified backups found on this media"}
    chosen = found[0]
    pv = preview(chosen["manifest"])
    print(f"backup: {chosen['backup']} ({chosen['files']} files, {pv['conflicts']} conflicts)")
    if input("Restore? [y/N]: ").strip().lower() == "y":
        from restore_transaction import restore
        return restore(chosen["backup"], root)
    return {"restored": False, "reason": "cancelled"}
