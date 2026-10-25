"""Notification store + dispatch to desktop toast / freedesktop daemon."""
from __future__ import annotations

import json
import sqlite3
import subprocess
import time
import uuid
from pathlib import Path

from aether_core import paths

DB = paths.SYSTEM_STATE_DIR / "notifications.db"


def _db() -> sqlite3.Connection:
    DB.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB)
    conn.execute("""CREATE TABLE IF NOT EXISTS notifications (
        id TEXT PRIMARY KEY, source TEXT, category TEXT, title TEXT, body TEXT,
        ts TEXT, read INTEGER DEFAULT 0)""")
    return conn


def notify(source: str, category: str, title: str, body: str = "") -> dict:
    nid = f"n-{uuid.uuid4().hex[:12]}"
    ts = time.strftime("%Y-%m-%dT%H:%M:%S%z")
    conn = _db()
    conn.execute("INSERT INTO notifications (id,source,category,title,body,ts) VALUES (?,?,?,?,?,?)",
                 (nid, source, category, title, body, ts))
    conn.commit()
    conn.close()
    _dispatch_to_session(title, body)
    _dispatch_freedesktop(title, body)
    return {"id": nid, "ts": ts}


def _dispatch_to_session(title: str, body: str) -> None:
    """Best-effort toast via the user shell."""
    try:
        import sys
        from pathlib import Path as _P
        sys.path.insert(0, str(_P(__file__).resolve().parents[2]))
        from service_main import SystemService
        SystemService("notifications", "notifications", {}).call_service(
            "shell", "Shell.toast", {"title": title, "body": body}, timeout=3)
    except Exception:
        pass


def _dispatch_freedesktop(title: str, body: str) -> None:
    """Best-effort forward to org.freedesktop.Notifications via gdbus."""
    try:
        subprocess.run(
            ["gdbus", "call", "--session", "--dest", "org.freedesktop.Notifications",
             "--object-path", "/org/freedesktop/Notifications",
             "--method", "org.freedesktop.Notifications.Notify",
             "Aether", "0", "dialog-information", title, body, "[]", "{}", "5000"],
            capture_output=True, timeout=5)
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass


def list_notifications(unread_only: bool = False) -> dict:
    conn = _db()
    q = "SELECT id,source,category,title,body,ts,read FROM notifications"
    if unread_only:
        q += " WHERE read=0"
    q += " ORDER BY ts DESC LIMIT 100"
    rows = conn.execute(q).fetchall()
    conn.close()
    return {"notifications": [
        {"id": r[0], "source": r[1], "category": r[2], "title": r[3],
         "body": r[4], "ts": r[5], "read": bool(r[6])} for r in rows]}


def close(notification_id: str) -> dict:
    conn = _db()
    conn.execute("UPDATE notifications SET read=1 WHERE id=?", (notification_id,))
    conn.commit()
    conn.close()
    return {"closed": notification_id}


def history(limit: int = 50) -> dict:
    return list_notifications()
