"""Logout flow: end the caller's session cleanly."""
from __future__ import annotations

import os
import subprocess


def logout() -> dict:
    uid = os.getuid()
    try:
        out = subprocess.run(["loginctl", "list-sessions", "--no-legend"],
                             capture_output=True, text=True, timeout=5)
        for line in out.stdout.splitlines():
            parts = line.split()
            if len(parts) >= 3 and parts[1] == str(uid):
                subprocess.run(["loginctl", "terminate-session", parts[0]], check=True, timeout=10)
                return {"logged_out": True, "session": parts[0]}
        return {"logged_out": False, "reason": "no session for current uid"}
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError) as e:
        return {"logged_out": False, "reason": str(e)}
