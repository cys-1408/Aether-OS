"""Real signature/integrity state from the package system."""
from __future__ import annotations

import subprocess


def signature_summary() -> str:
    try:
        out = subprocess.run(["pacman-key", "--list-keys"], capture_output=True, text=True, timeout=15)
        n = len([l for l in out.stdout.splitlines() if l.startswith("pub")])
        conf = subprocess.run(["grep", "SigLevel", "/etc/pacman.conf"], capture_output=True, text=True, timeout=5)
        return f"keyring: {n} keys · SigLevel: {conf.stdout.strip().splitlines()[0] if conf.stdout else 'default'}"
    except FileNotFoundError:
        return "pacman-key not installed"
