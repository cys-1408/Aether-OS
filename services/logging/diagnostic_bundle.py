"""Redacted diagnostic bundle — requires explicit consent."""
from __future__ import annotations

import gzip
import hashlib
import io
import json
import subprocess
import tarfile
import time
import uuid
from pathlib import Path

from aether_core.logging_setup import redact_text
from aether_core import paths


def create(scope: list[str], consent: bool) -> dict:
    if not consent:
        return {"created": False, "reason": "E_CONSENT_REQUIRED: explicit consent required"}
    scope = scope or ["unit_states", "kernel_version", "hardware_summary"]
    buf = io.BytesIO()
    redactions = 0
    with tarfile.open(fileobj=buf, mode="w:gz") as tar:
        def add_text(name: str, text: str):
            nonlocal redactions
            red = redact_text(text)
            redactions += 0 if red == text else 1
            data = red.encode()
            info = tarfile.TarInfo(name=f"aether-diagnostics/{name}")
            info.size = len(data)
            tar.addfile(info, io.BytesIO(data))

        if "kernel_version" in scope:
            try:
                kv = subprocess.run(["uname", "-a"], capture_output=True, text=True, timeout=5).stdout
                add_text("kernel.txt", kv)
            except subprocess.TimeoutExpired:
                pass
        if "unit_states" in scope:
            try:
                us = subprocess.run(["systemctl", "list-units", "--failed", "--no-pager"],
                                    capture_output=True, text=True, timeout=10).stdout
                add_text("failed-units.txt", us)
            except (FileNotFoundError, subprocess.TimeoutExpired):
                pass
        if "hardware_summary" in scope:
            add_text("hardware.txt", Path("/proc/cpuinfo").read_text()[:4000])
        if "failed_units_journal_200_lines" in scope:
            try:
                j = subprocess.run(["journalctl", "-p", "err", "-n", "200", "--no-pager"],
                                   capture_output=True, text=True, timeout=15).stdout
                add_text("journal-errors.txt", j)
            except (FileNotFoundError, subprocess.TimeoutExpired):
                pass
    blob = buf.getvalue()
    out = paths.USER_STATE_DIR / f"aether-diagnostics-{time.strftime('%Y%m%d-%H%M%S')}.tar.gz"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(blob)
    meta = {
        "bundle_id": f"diag-{uuid.uuid4().hex[:10]}",
        "created_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "consent": True, "scope": scope,
        "files": [{"path": "aether-diagnostics/", "redactions_applied": redactions}],
        "redactions_applied": redactions,
        "sha256": hashlib.sha256(blob).hexdigest(),
    }
    (out.parent / (out.name + ".json")).write_text(json.dumps(meta, indent=2))
    return {"created": True, "file": str(out), "metadata": meta}
