"""journald query via journalctl (structured, redacted)."""
from __future__ import annotations

import json
import subprocess

from aether_core.logging_setup import redact_text


def query(*, unit: str | None = None, since: str | None = None, until: str | None = None,
          priority: int | None = None, contains: str | None = None, lines: int = 200) -> dict:
    argv = ["journalctl", "-o", "json", "--no-pager", "-n", str(min(2000, max(1, lines)))]
    if unit:
        argv += ["-u", unit]
    if since:
        argv += ["--since", since]
    if until:
        argv += ["--until", until]
    if priority is not None:
        argv += ["-p", str(priority)]
    try:
        out = subprocess.run(argv, capture_output=True, text=True, timeout=20)
    except (FileNotFoundError, subprocess.TimeoutExpired) as e:
        return {"entries": [], "reason": str(e)}
    entries = []
    for line in out.stdout.splitlines():
        try:
            rec = json.loads(line)
        except json.JSONDecodeError:
            continue
        msg = rec.get("MESSAGE", "")
        if contains and contains.lower() not in str(msg).lower():
            continue
        entries.append({
            "ts": rec.get("__REALTIME_TIMESTAMP"), "unit": rec.get("_SYSTEMD_UNIT"),
            "priority": rec.get("PRIORITY"), "message": redact_text(str(msg)[:2000]),
        })
    return {"entries": entries}
