"""Process action policy: own-process SIGTERM; others via pkexec."""
from __future__ import annotations

import os
import signal
import subprocess


def terminate(pid: int) -> dict:
    try:
        owner = os.stat(f"/proc/{pid}").st_uid
    except OSError:
        return {"ok": False, "error": "process gone"}
    try:
        if owner == os.getuid():
            os.kill(pid, signal.SIGTERM)
            return {"ok": True, "signal": "SIGTERM"}
        out = subprocess.run(["pkexec", "kill", str(pid)], capture_output=True, timeout=10)
        return {"ok": out.returncode == 0, "signal": "SIGTERM (pkexec)"}
    except (PermissionError, FileNotFoundError, subprocess.TimeoutExpired) as e:
        return {"ok": False, "error": str(e)}
