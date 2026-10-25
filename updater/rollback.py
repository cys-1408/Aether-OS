"""Updater-side rollback coordination (delegates to package rollback)."""
from __future__ import annotations


def rollback() -> dict:
    sys_path = __import__("pathlib").Path(__file__).resolve().parents[1] / "package-manager"
    import sys
    sys.path.insert(0, str(sys_path))
    from core.package_manager import rollback_last
    return rollback_last()
