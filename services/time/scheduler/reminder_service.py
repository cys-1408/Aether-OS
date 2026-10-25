"""Persistent reminders with explicit user intent; fires real notifications."""
from __future__ import annotations

import json
import sqlite3
import threading
import time
from pathlib import Path

from aether_core import paths
from aether_core.errors import IpcError
from datetime import datetime, timezone

DB = paths.USER_STATE_DIR / "reminders.db"


def _db() -> sqlite3.Connection:
    DB.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB)
    conn.execute("""CREATE TABLE IF NOT EXISTS reminders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        due_utc TEXT NOT NULL,
        created_at TEXT NOT NULL,
        notified INTEGER DEFAULT 0)""")
    return conn


def add(title: str, due_iso: str) -> dict:
    if not title.strip():
        raise IpcError("E_INVALID", "reminder title required")
    datetime.fromisoformat(due_iso)  # validate
    conn = _db()
    cur = conn.execute("INSERT INTO reminders (title, due_utc, created_at) VALUES (?,?,?)",
                       (title.strip(), due_iso, datetime.now(timezone.utc).isoformat()))
    conn.commit()
    rid = cur.lastrowid
    conn.close()
    return {"id": rid, "title": title.strip(), "due_utc": due_iso}


def list_reminders() -> dict:
    conn = _db()
    rows = conn.execute("SELECT id,title,due_utc,created_at,notified FROM reminders ORDER BY due_utc").fetchall()
    conn.close()
    return {"reminders": [{"id": r[0], "title": r[1], "due_utc": r[2],
                           "created_at": r[3], "notified": bool(r[4])} for r in rows]}


def remove(reminder_id: int) -> dict:
    conn = _db()
    conn.execute("DELETE FROM reminders WHERE id=?", (int(reminder_id),))
    conn.commit()
    conn.close()
    return {"removed": int(reminder_id)}


class ReminderFire(threading.Thread):
    """Background thread: fire due reminders as real notifications."""

    def __init__(self, notify_sock: str):
        super().__init__(daemon=True)
        self.notify_sock = notify_sock

    def run(self) -> None:
        while True:
            try:
                conn = _db()
                rows = conn.execute(
                    "SELECT id,title FROM reminders WHERE notified=0 AND due_utc <= ?",
                    (datetime.now(timezone.utc).isoformat(),)).fetchall()
                for rid, title in rows:
                    self._notify(title)
                    conn.execute("UPDATE reminders SET notified=1 WHERE id=?", (rid,))
                conn.commit()
                conn.close()
            except Exception:
                pass
            time.sleep(15)

    def _notify(self, title: str) -> None:
        import sys
        from pathlib import Path as _P
        sys.path.insert(0, str(_P(__file__).resolve().parents[2]))
        from service_main import SystemService
        SystemService("reminders", "reminders", {}).call_service(
            "notifications", "Notify.notify",
            {"source": "reminders", "category": "reminder", "title": "Reminder", "body": title})
