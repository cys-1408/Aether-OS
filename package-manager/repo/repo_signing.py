"""Repo signing helper (key handling per release/signing-policy.md)."""
from __future__ import annotations

import subprocess


def sign_db(db_path: str, key: str | None = None) -> dict:
    argv = ["gpg", "--detach-sign"]
    if key:
        argv += ["-u", key]
    argv.append(db_path)
    out = subprocess.run(argv, capture_output=True, text=True, timeout=60)
    return {"signed": out.returncode == 0}
