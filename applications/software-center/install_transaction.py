"""Install/remove via the privileged aether-pm helper (pkexec)."""
from __future__ import annotations

import subprocess

HELPER = "/usr/libexec/aether/aether-pm"


def install(name: str) -> str:
    try:
        out = subprocess.run(["pkexec", HELPER, "install", name],
                             capture_output=True, text=True, timeout=3600)
        return out.stdout.strip()[-200:] if out.returncode == 0 else f"failed: {out.stderr.strip()[-200:]}"
    except FileNotFoundError:
        return "pkexec/aether-pm not available"


def uninstall(name: str) -> str:
    try:
        out = subprocess.run(["pkexec", HELPER, "remove", name],
                             capture_output=True, text=True, timeout=3600)
        return out.stdout.strip()[-200:] if out.returncode == 0 else f"failed: {out.stderr.strip()[-200:]}"
    except FileNotFoundError:
        return "pkexec/aether-pm not available"
