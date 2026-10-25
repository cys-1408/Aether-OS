"""Model update rollback: restore the previous catalog/artifact when retained."""
from __future__ import annotations

import shutil
from pathlib import Path

CATALOG_DIR = Path("/var/lib/aether/runtime/catalog")
BACKUP_SUFFIX = ".previous"


def catalog_rollback() -> dict:
    current = CATALOG_DIR / "catalog.json"
    backup = CATALOG_DIR / ("catalog.json" + BACKUP_SUFFIX)
    if not backup.exists():
        return {"rolled_back": False,
                "reason": "no previous catalog retained; nothing to revert"}
    if not current.exists():
        # The previous copy IS the state we want back.
        shutil.copy2(backup, current)
        return {"rolled_back": True, "restored": True}
    shutil.copy2(backup, current)
    return {"rolled_back": True, "restored": True}


def artifact_rollback(model_id: str) -> dict:
    """Revert to the previous model artifact directory when retained."""
    store = CATALOG_DIR.parent / "models" / model_id
    prev = store.with_name(store.name + BACKUP_SUFFIX)
    if not prev.exists():
        return {"rolled_back": False, "model_id": model_id,
                "reason": "previous artifact not retained"}
    # Current may be active; swap only with the runtime stopped (honest, so
    # we refuse rather than unload silently from the updater path).
    if (store / "locked").exists():
        return {"rolled_back": False, "model_id": model_id,
                "reason": "model in use; stop it in the Runtime before rollback"}
    shutil.rmtree(store, ignore_errors=True)
    prev.rename(store)
    return {"rolled_back": True, "model_id": model_id}
