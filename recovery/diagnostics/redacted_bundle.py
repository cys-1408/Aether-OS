"""Redacted diagnostics bundle: collect, scrub, tar.gz."""

from __future__ import annotations

import io
import json
import re
import tarfile
import time
from pathlib import Path

from .collect_system_state import collect_system_state

DEFAULT_BUNDLE_PATH = Path("/var/lib/aether/recovery/diagnostic-bundle.tar.gz")

REDACTION_RULES = [
    ("ipv4", re.compile(r"\b(?!\d+\.\d+\.\d+\.\d+$)(?:\d{1,3}\.){3}\d{1,3}\b"),
     "<IP>"),
    ("mac", re.compile(r"\b([0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}\b"), "<MAC>"),
    ("email", re.compile(r"\b[\w.+-]+@[\w-]+\.[\w.]+\b"), "<EMAIL>"),
    ("ssid", re.compile(r"(?i)\b(ssid\s*[=:]\s*)\S+"), r"\1<SSID>"),
    ("machine_id", re.compile(r"\b[0-9a-f]{32}\b"), "<MACHINE_ID>"),
    ("passphrase_kv", re.compile(
        r"(?i)\b(passphrase|password|secret|token)\b(\s*[=:]\s*)\S+"),
     r"\1\2<REDACTED>"),
]


def redact_line(text: str) -> str:
    for _name, pattern, repl in REDACTION_RULES:
        text = pattern.sub(repl, text)
    return text


def redact_object(obj):
    if isinstance(obj, str):
        return redact_line(obj)
    if isinstance(obj, list):
        return [redact_object(item) for item in obj]
    if isinstance(obj, dict):
        return {key: redact_object(value) for key, value in obj.items()}
    return obj


def build_redacted_bundle(destination: Path | None = None,
                          *, include_logs: bool = True) -> dict:
    """Collect diagnostics, apply redactions, and write a tar.gz bundle.

    Returns {"path": ..., "entries": [...], "bytes": n}. Never includes
    unredacted content.
    """
    destination = Path(destination) if destination else DEFAULT_BUNDLE_PATH
    destination.parent.mkdir(parents=True, exist_ok=True)

    payload = redact_object(collect_system_state())
    staged: list[tuple[str, bytes]] = [
        ("diagnostics/system-state.json",
         json.dumps(payload, indent=2, sort_keys=True, default=str).encode("utf-8")),
    ]
    if include_logs:
        for log_path, arcname in (
            (Path("/var/log/aether/installer.log"), "logs/installer.log"),
            (Path("/run/aether/recovery/session.journal.jsonl"),
             "logs/recovery-session.jsonl"),
            (Path("/var/lib/aether/pm/transactions.db"), None),
        ):
            if arcname is None:
                continue  # sqlite db skipped: contains package paths pre-redaction
            if log_path.is_file():
                text = log_path.read_text(encoding="utf-8", errors="replace")
                cleaned = "\n".join(redact_line(l) for l in text.splitlines())
                staged.append((arcname, (cleaned + "\n").encode("utf-8")))

    import os

    with tarfile.open(destination, "w:gz") as tar:
        for arcname, blob in staged:
            info = tarfile.TarInfo(name=arcname)
            info.size = len(blob)
            info.mtime = int(time.time())
            info.mode = 0o600
            tar.addfile(info, io.BytesIO(blob))
    os.chmod(destination, 0o600)
    return {"path": str(destination), "entries": [a for a, _ in staged],
            "bytes": destination.stat().st_size}
