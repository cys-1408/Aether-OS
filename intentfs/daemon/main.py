import sys
from pathlib import Path
_p = Path(__file__).resolve()
sys.path.insert(0, str(_p.parents[3] / 'libraries/libaether-core/python'))
"""aether-intentfs daemon entry (per-user index DBs; per-uid scoping)."""
from intentfs_service import IntentFSService  # noqa: E402
from aether_core.ipc import JsonRpcServer  # noqa: E402
from aether_core.config import load_yaml  # noqa: E402
from aether_core import paths  # noqa: E402
from aether_core.logging_setup import configure_logging  # noqa: E402
from aether_core.errors import IpcError  # noqa: E402

sys.path.insert(0, str(_p.parent))
sys.path.insert(0, str(_p.parents[1] / "watcher"))
sys.path.insert(0, str(_p.parents[1] / "pipeline"))
sys.path.insert(0, str(_p.parents[1] / "index"))
sys.path.insert(0, str(_p.parents[1] / "search"))
sys.path.insert(0, str(_p.parents[1] / "extraction"))
sys.path.insert(0, str(_p.parents[1] / "concepts"))
sys.path.insert(0, str(_p.parents[1] / "privacy"))

from filesystem_watcher import Watcher  # noqa: E402
from metadata_store import MetadataStore  # noqa: E402
from job_scheduler import JobScheduler  # noqa: E402
from search_service import SearchService  # noqa: E402
from folder_exclusions import excluded  # noqa: E402
import mime_detection  # noqa: E402

log = configure_logging("intentfs")


def _store_for(uid: int) -> MetadataStore:
    """Per-user SQLite DB under the user's state dir (per_user_scope)."""
    import pwd
    try:
        home = Path(pwd.getpwuid(uid).pw_dir)
    except KeyError:
        raise IpcError("E_NOT_FOUND", f"uid {uid} unknown")
    db = home / ".local/share/aether/intentfs/intentfs.db"
    return MetadataStore(db)


def build_server() -> JsonRpcServer:
    config = load_yaml("/etc/aether/intentfs.yaml") or {}
    svc = IntentFSService(config)
    scheduler = JobScheduler(config)
    watcher = Watcher(config, scheduler)
    watcher.start()

    def uid_of(params: dict) -> int:
        import os
        return int(params.get("uid", os.getuid()))

    def search(params: dict) -> dict:
        store = _store_for(uid_of(params))
        engine = SearchService(store, config)
        return engine.search(str(params.get("query", "")), dict(params.get("filters", {})))

    def metadata(params: dict) -> dict:
        store = _store_for(uid_of(params))
        rec = store.get_by_path(str(params.get("path", "")))
        if not rec:
            raise IpcError("E_NOT_FOUND", "no index record for path")
        return rec

    def concepts(params: dict) -> dict:
        store = _store_for(uid_of(params))
        rec = store.get_by_path(str(params.get("path", "")))
        if not rec:
            raise IpcError("E_NOT_FOUND", "no index record")
        return {"index_status": rec["index_status"],
                "concepts": rec.get("concepts") if rec["index_status"] == "ready" else None,
                "failure_reason": rec.get("failure_reason")}

    methods = {
        "IntentFS.search": search,
        "IntentFS.metadata": metadata,
        "IntentFS.concepts": concepts,
        "IntentFS.status": lambda p: svc.status(),
        "IntentFS.pause": lambda p: svc.set_paused(True),
        "IntentFS.resume": lambda p: svc.set_paused(False),
        "IntentFS.reindex": lambda p: scheduler.reindex(str(p.get("path", "")), _store_for(uid_of(p))),
        "IntentFS.clear": lambda p: _clear(str(p.get("scope", "all")), _store_for(uid_of(p))),
        "IntentFS.exclusions_get": lambda p: {"exclusions": config.get("exclusions", [])},
        "IntentFS.exclusions_set": lambda p: {"exclusions": list(p.get("exclusions", []))},
    }
    return JsonRpcServer(paths.system_socket("intentfs"), methods)


def _clear(scope: str, store: MetadataStore) -> dict:
    """INDEX-ONLY deletion — original files are never touched (enforced here)."""
    cleared = store.clear_all()
    return {"cleared": cleared, "scope": scope,
            "note": "index data only; source files untouched"}


if __name__ == "__main__":
    server = build_server()
    log.info("aether-intentfs listening")
    server.serve_forever()
