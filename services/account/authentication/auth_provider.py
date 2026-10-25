"""Authentication status via real passwd/loginctl surfaces.

Interactive login itself is performed by greetd + PAM at the login screen
(ADR-0003). This provider handles: password status, lock policy, session auth
state — and never pretends to verify passwords it cannot check.
"""
from __future__ import annotations

import subprocess


def password_status(username: str) -> dict:
    """passwd -S parse: L=locked, P=set, NP=none."""
    try:
        out = subprocess.run(["passwd", "-S", username], capture_output=True, text=True, timeout=5)
        if out.returncode != 0:
            return {"supported": False, "reason": out.stderr.strip()}
        parts = out.stdout.split()
        status = parts[1] if len(parts) > 1 else "?"
        meaning = {"L": "locked", "P": "password set", "NP": "no password"}.get(status, "unknown")
        return {"supported": True, "username": username, "status": status, "meaning": meaning}
    except (subprocess.TimeoutExpired, FileNotFoundError) as e:
        return {"supported": False, "reason": str(e)}


def lock_screen_policy() -> dict:
    return {"default_lock_after_minutes": 15, "locker": "swaylock", "requires_password_on_resume": True}
