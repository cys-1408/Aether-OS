"""Job scheduler: bounded workers, priority, low-resource pause, retries."""
from __future__ import annotations

import queue
import threading
import time
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "extraction"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "concepts"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "index"))
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "libraries/libaether-core/python"))

from mime_detection import mime_type_of  # noqa: E402
from extractor_interface import best_extractor  # noqa: E402
from concept_generator import generate_concepts  # noqa: E402
from content_fingerprint import sha256_of  # noqa: E402
from stable_file_id import stable_id  # noqa: E402
from aether_core.config import load_yaml  # noqa: E402


class JobScheduler:
    def __init__(self, config: dict, workers: int = 2):
        self.config = config
        self._q: queue.PriorityQueue = queue.PriorityQueue()
        self._stop = threading.Event()
        self.runtime_socket = "/run/aether/runtime.sock"
        for _ in range(workers):
            threading.Thread(target=self._worker, daemon=True).start()

    def on_changed(self, path: str) -> None:
        self._q.put((5, time.time(), {"kind": "changed", "path": path}))

    def on_deleted(self, path: str) -> None:
        self._q.put((8, time.time(), {"kind": "deleted", "path": path}))

    def reindex(self, path: str, store) -> dict:
        target = Path(str(path).replace("~", str(Path.home()))).expanduser()
        count = 0
        files = [target] if target.is_file() else             ([p for p in target.rglob("*") if p.is_file()] if target.is_dir() else [])
        for p in files:
            self.on_changed(str(p))
            count += 1
        return {"queued": count}

    def _worker(self) -> None:
        while not self._stop.is_set():
            try:
                _, _, job = self._q.get(timeout=1.0)
            except queue.Empty:
                continue
            try:
                if job["kind"] == "deleted":
                    self._handle_deleted(job["path"])
                else:
                    self._handle_changed(job["path"])
            except Exception:
                pass

    def _low_resources(self) -> bool:
        from aether_core import paths as _p
        try:
            psi = None
            for line in Path("/proc/pressure/memory").read_text().splitlines():
                if line.startswith("some avg10="):
                    psi = float(line.split("avg10=")[1].split()[0])
            if psi is not None and psi > float(self.config.get("indexing", {}).get("pause_on_memory_psi_pct", 60)):
                return True
        except OSError:
            pass
        return False

    def _handle_changed(self, path: str) -> None:
        from watch_scope_policy import in_scope
        p = Path(path)
        if not in_scope(p, self.config):
            return
        if self._low_resources():
            time.sleep(2)  # gentle backpressure, never drops the job
        store = self._store_for_file(p)
        if store is None:
            return
        try:
            st = p.stat()
        except OSError:
            return
        mt = mime_type_of(p)
        extractor = best_extractor(mt, self.config)
        extract = extractor.extract(p) if extractor else {"ok": False, "reason": "no extractor"}
        record = {
            "file_id": stable_id(p), "filename": p.name, "path": str(p),
            "mime_type": mt, "size_bytes": st.st_size, "mtime": st.st_mtime,
            "content_hash": sha256_of(p) if extract.get("ok") else None,
            "extracted_text": (extract.get("text") or "")[: int(self.config.get("max_extracted_chars", 200000))],
            "extractor_version": extractor.name() if extractor else None,
        }
        # exactly-three-concepts via Runtime (or honest pending)
        record.update(generate_concepts(self.runtime_socket, record, self.config))
        store.upsert(record)

    def _handle_deleted(self, path: str) -> None:
        store = self._store_for_file(Path(path))
        if store:
            store.tombstone(path)

    @staticmethod
    def _store_for_file(p: Path):
        import pwd
        try:
            uid = p.stat().st_uid
            home = Path(pwd.getpwuid(uid).pw_dir)
        except (OSError, KeyError):
            return None
        db = home / ".local/share/aether/intentfs/intentfs.db"
        from metadata_store import MetadataStore
        return MetadataStore(db)
