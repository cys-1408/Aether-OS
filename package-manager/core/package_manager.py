"""aether-pm core: journal + staged pacman transactions."""
from __future__ import annotations

import json
import sqlite3
import subprocess
import time
from pathlib import Path

from aether_core import paths
from aether_core.errors import IpcError

DB = paths.SYSTEM_STATE_DIR / "pm" / "transactions.db"


def _db() -> sqlite3.Connection:
    DB.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB)
    conn.execute("""CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT, ts TEXT, action TEXT,
        packages TEXT, result TEXT, detail TEXT)""")
    return conn


def _journal(action: str, packages: list[str], result: str, detail: str = "") -> int:
    with _db() as conn:
        with conn:
            cur = conn.execute("INSERT INTO transactions (ts,action,packages,result,detail) VALUES (?,?,?,?,?)",
                               (time.strftime("%Y-%m-%dT%H:%M:%S%z"), action, " ".join(packages), result, detail[:400]))
            return cur.lastrowid


def _pacman(argv: list[str], timeout: int = 3600) -> subprocess.CompletedProcess:
    return subprocess.run(["pacman", *argv], capture_output=True, text=True, timeout=timeout)


def install(packages: list[str]) -> dict:
    if not packages:
        raise IpcError("E_INVALID", "no packages given")
    pre = _pacman(["-T", *packages])
    stage = _pacman(["-Sw", "--noconfirm", *packages])
    if stage.returncode != 0:
        _journal("install", packages, "failed-download", stage.stderr)
        raise IpcError("E_DOWNLOAD", stage.stderr[-200:])
    apply = _pacman(["-S", "--noconfirm", *packages])
    result = "ok" if apply.returncode == 0 else "failed"
    _journal("install", packages, result, apply.stderr[-200:])
    if apply.returncode != 0:
        raise IpcError("E_INSTALL", apply.stderr[-200:])
    return {"ok": True, "packages": packages}


def remove(packages: list[str]) -> dict:
    apply = _pacman(["-R", "--noconfirm", *packages])
    result = "ok" if apply.returncode == 0 else "failed"
    _journal("remove", packages, result, apply.stderr[-200:])
    if apply.returncode != 0:
        raise IpcError("E_REMOVE", apply.stderr[-200:])
    return {"ok": True, "packages": packages}


def update_all() -> dict:
    apply = _pacman(["-Su", "--noconfirm"])
    result = "ok" if apply.returncode == 0 else "failed"
    _journal("update", [], result, apply.stdout[-200:])
    return {"ok": apply.returncode == 0, "detail": apply.stdout[-400:]}


def search(query: str) -> list[dict]:
    out = _pacman(["-Sl"], timeout=60)
    return [{"repo": p[0], "name": p[1], "version": p[2]}
            for p in (l.split() for l in out.stdout.splitlines() if l.strip())
            if not query or query.lower() in p[1].lower()]


def installed() -> list[str]:
    out = _pacman(["-Qq"], timeout=60)
    return out.stdout.split()


def info(name: str) -> dict:
    out = _pacman(["-Si", name], timeout=30)
    fields = {}
    for line in out.stdout.splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            fields[k.strip()] = v.strip()
    return fields


def history(limit: int = 20) -> list[dict]:
    with _db() as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute("SELECT * FROM transactions ORDER BY id DESC LIMIT ?", (limit,)).fetchall()
    return [dict(r) for r in rows]


def rollback_last() -> dict:
    with _db() as conn:
        conn.row_factory = sqlite3.Row
        row = conn.execute("SELECT * FROM transactions WHERE action IN ('install','update') AND result='ok' ORDER BY id DESC LIMIT 1").fetchone()
    if not row:
        return {"rolled_back": False, "reason": "no reversible transaction"}
    pkgs = row["packages"].split()
    cache = Path("/var/cache/pacman/pkg")
    # find previous cached versions for downgrade
    out = subprocess.run(["pacman", "-U", "--noconfirm", *[str(p) for p in sorted(cache.glob(f"{pkgs[0]}-[0-9]*.pkg.tar.*"))[:1]]],
                         capture_output=True, text=True, timeout=1800)
    _journal("rollback", pkgs, "ok" if out.returncode == 0 else "failed")
    return {"rolled_back": out.returncode == 0, "packages": pkgs}
