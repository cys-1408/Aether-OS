"""User creation via the polkit account helper (strict argv, no shell)."""
from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

HELPER = "/usr/libexec/aether/aether-account-helper"
USERNAME_RE = re.compile(r"^[a-z_][a-z0-9_-]{0,31}$")

TOP_1000 = {"password", "123456", "qwerty", "letmein", "admin", "welcome",
            "monkey", "dragon", "football", "iloveyou", "abc123", "111111"}


def validate_username(username: str) -> None:
    if not USERNAME_RE.match(username):
        raise ValueError(f"invalid username: {username!r} (lowercase, start letter/underscore, <=32 chars)")


def password_score(password: str) -> dict:
    score = 0
    if len(password) >= 8:
        score += 1
    if len(password) >= 12:
        score += 1
    if re.search(r"[a-z]", password) and re.search(r"[A-Z]", password):
        score += 1
    if re.search(r"[0-9]", password):
        score += 1
    if re.search(r"[^A-Za-z0-9]", password):
        score += 1
    if password.lower() in TOP_1000:
        score = 0
    return {"score": score, "acceptable": score >= 3, "max": 5}


def validate_password(password: str) -> None:
    if len(password) < 8:
        raise ValueError("password must be at least 8 characters")
    if password.lower() in TOP_1000:
        raise ValueError("password is in the common-password list")


def create_user(username: str, full_name: str, password: str, admin: bool) -> dict:
    """Create a user through the polkit helper; helper validates + logs."""
    validate_username(username)
    validate_password(password)
    full_name = full_name.replace(",", " ")[:64]  # GECOS comma safety
    argv = [HELPER, "create-user", username, full_name, "yes" if admin else "no"]
    proc = subprocess.run(argv, input=password + "\n" + password + "\n",
                          capture_output=True, text=True, timeout=30)
    if proc.returncode != 0:
        return {"ok": False, "error": proc.stderr.strip() or proc.stdout.strip() or "helper failed"}
    return {"ok": True, "username": username, "admin": admin}


def set_password(username: str, password: str) -> dict:
    validate_username(username)
    validate_password(password)
    proc = subprocess.run([HELPER, "set-password", username],
                          input=password + "\n" + password + "\n",
                          capture_output=True, text=True, timeout=30)
    return {"ok": proc.returncode == 0, "error": None if proc.returncode == 0 else proc.stderr.strip()}
