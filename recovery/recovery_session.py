"""Recovery session: environment, selected system, action journal."""

from __future__ import annotations

import json
import time
from pathlib import Path

from ._process import is_root

# "recovery-entry" contains a hyphen and cannot use the import statement;
# importlib loads it by exact module path.
import importlib

_system_detection = importlib.import_module("recovery.recovery-entry.system_detection")
detect_installed_systems = _system_detection.detect_installed_systems
mount_installed_system = _system_detection.mount_installed_system
unmount_installed_system = _system_detection.unmount_installed_system
unmount_probe_mounts = _system_detection.unmount_probe_mounts

SESSION_DIR = Path("/run/aether/recovery")
SESSION_JOURNAL = SESSION_DIR / "session.journal.jsonl"


class RecoverySession:
    """One recovery run: detection, optional system mount, action journal."""

    def __init__(self, *, dry_run: bool = False, require_root: bool = True):
        self.dry_run = dry_run
        if require_root and not is_root() and not dry_run:
            raise PermissionError(
                "the recovery environment runs as root; boot "
                "aether-recovery.target or run from the live ISO root shell"
            )
        self.system: dict | None = None
        self.systems: list[dict] = []
        self._journal: list[dict] = []

    # ------------------------------------------------------------------ #
    def detect(self) -> list[dict]:
        try:
            self.systems = detect_installed_systems()
        except RuntimeError as exc:
            self._record("detect_failed", error=str(exc))
            self.systems = []
        return self.systems

    def select_system(self, device: str) -> dict:
        match = [s for s in self.systems if s["device"] == device]
        if not match:
            raise ValueError(f"no detected system on {device}; run detect() first")
        self.system = match[0]
        self._record("system_selected", device=device,
                     is_aether=self.system.get("is_aether"))
        return self.system

    def mount_selected(self, *, read_only: bool = False) -> dict:
        if not self.system:
            raise RuntimeError("no system selected")
        result = mount_installed_system(self.system["device"],
                                        read_only=read_only)
        self._record("system_mounted", **result)
        return result

    def unmount_selected(self) -> dict:
        result = unmount_installed_system()
        self._record("system_unmounted", ok=result["unmounted"])
        return result

    def release_probes(self) -> list[str]:
        return unmount_probe_mounts()

    # ------------------------------------------------------------------ #
    def record_action(self, action: str, **fields) -> None:
        self._record(action, **fields)

    def _record(self, event: str, **fields) -> None:
        entry = {"ts": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
                 "event": event, "fields": fields}
        self._journal.append(entry)
        if not self.dry_run:
            try:
                SESSION_DIR.mkdir(parents=True, exist_ok=True)
                with open(SESSION_JOURNAL, "a", encoding="utf-8") as fh:
                    fh.write(json.dumps(entry, sort_keys=True, default=str) + "\n")
            except OSError:
                pass

    @property
    def journal(self) -> list[dict]:
        return list(self._journal)

    def status_summary(self) -> dict:
        return {
            "root": is_root(),
            "dry_run": self.dry_run,
            "detected_systems": len(self.systems),
            "selected": (self.system or {}).get("device"),
            "actions": len(self._journal),
        }
