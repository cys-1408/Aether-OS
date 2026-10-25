"""Session auth state via loginctl."""
from __future__ import annotations

import os
import subprocess


def current_session() -> dict:
    uid = os.getuid()
    try:
        out = subprocess.run(["loginctl", "list-sessions", "--no-legend"],
                             capture_output=True, text=True, timeout=5)
        sessions = []
        for line in out.stdout.splitlines():
            parts = line.split()
            if len(parts) >= 3:
                sessions.append({"id": parts[0], "uid": int(parts[1]), "user": parts[2]})
        mine = [s for s in sessions if s["uid"] == uid]
        return {"supported": True, "session": mine[0] if mine else None, "all": sessions}
    except (subprocess.TimeoutExpired, FileNotFoundError, ValueError) as e:
        return {"supported": False, "reason": str(e)}
