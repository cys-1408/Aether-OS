"""Conversation persistence (sqlite, per user)."""
from __future__ import annotations

import sqlite3
import time

from aether_core import paths

DB = paths.USER_STATE_DIR / "miso-conversation.db"


class ConversationState:
    def __init__(self):
        DB.parent.mkdir(parents=True, exist_ok=True)
        self._db = DB

    def _conn(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self._db)
        conn.execute("""CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT, who TEXT, text TEXT, ts TEXT)""")
        return conn

    def append(self, who: str, text: str) -> None:
        with self._conn() as conn:
            with conn:
                conn.execute("INSERT INTO messages (who,text,ts) VALUES (?,?,?)",
                             (who, text[:4000], time.strftime("%Y-%m-%dT%H:%M:%S%z")))

    def history(self, limit: int = 50) -> dict:
        with self._conn() as conn:
            rows = conn.execute("SELECT who,text,ts FROM messages ORDER BY id DESC LIMIT ?",
                                (limit,)).fetchall()
        return {"messages": [{"who": r[0], "text": r[1], "ts": r[2]} for r in reversed(rows)]}
