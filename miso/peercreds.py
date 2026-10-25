"""Peer credential helpers for unix domain sockets.

Uses SO_PEERCRED (Linux) to identify the process on the other end of a
connection and reads the systemd unit name from /proc/<pid>/cgroup. This is
the basis of broker, ledger and workspace request authentication.
"""

from __future__ import annotations

import pwd
import socket
import struct
from pathlib import Path


def get_peer_credentials(conn: socket.socket) -> dict:
    """Return {"pid", "uid", "gid"} for the peer behind ``conn``."""
    creds = conn.getsockopt(socket.SOL_SOCKET, socket.SO_PEERCRED, struct.calcsize("3i"))
    pid, uid, gid = struct.unpack("3i", creds)
    return {"pid": int(pid), "uid": int(uid), "gid": int(gid)}


def username_for(uid: int) -> str | None:
    """Resolve a uid to a username, or None when the uid has no passwd entry."""
    try:
        return pwd.getpwuid(uid).pw_name
    except KeyError:
        return None


def unit_for_pid(pid: int) -> str | None:
    """Best-effort systemd unit name for a pid (cgroup v1/v2), or None."""
    if pid <= 0:
        return None
    try:
        text = Path(f"/proc/{int(pid)}/cgroup").read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None
    for line in text.splitlines():
        parts = line.split(":", 2)
        if len(parts) != 3:
            continue
        cgroup_path = parts[2].strip()
        if not cgroup_path:
            continue
        name = cgroup_path.rsplit("/", 1)[-1]
        if name.endswith(".service"):
            return name
    return None


def enrich_peer(creds: dict) -> dict:
    """Add username and systemd unit (best effort) to raw SO_PEERCRED output."""
    peer = dict(creds)
    peer["username"] = username_for(creds.get("uid", -1))
    peer["unit"] = unit_for_pid(creds.get("pid", -1))
    return peer
