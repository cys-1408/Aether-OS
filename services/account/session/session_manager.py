"""Real session management via systemd-logind."""
from __future__ import annotations

import subprocess


def list_sessions() -> dict:
    try:
        out = subprocess.run(["loginctl", "list-sessions", "--no-legend"],
                             capture_output=True, text=True, timeout=5)
        sessions = []
        for line in out.stdout.splitlines():
            parts = line.split()
            if len(parts) >= 3:
                sessions.append({"id": parts[0], "uid": int(parts[1]), "user": parts[2],
                                 "seat": parts[3] if len(parts) > 3 else None})
        return {"sessions": sessions}
    except (subprocess.TimeoutExpired, FileNotFoundError) as e:
        return {"sessions": [], "reason": str(e)}


def show_session(session_id: str) -> dict:
    try:
        out = subprocess.run(["loginctl", "show-session", session_id],
                             capture_output=True, text=True, timeout=5)
        props = {}
        for line in out.stdout.splitlines():
            if "=" in line:
                k, v = line.split("=", 1)
                props[k] = v
        return {"session": props}
    except (subprocess.TimeoutExpired, FileNotFoundError) as e:
        return {"reason": str(e)}


def terminate(session_id: str) -> dict:
    try:
        subprocess.run(["loginctl", "terminate-session", session_id], check=True, timeout=10)
        return {"terminated": session_id}
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError) as e:
        return {"error": str(e)}
