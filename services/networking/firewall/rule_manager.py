"""Validated rule operations (only enumerated verbs/fields accepted)."""
from __future__ import annotations

import subprocess

HELPER = "/usr/libexec/aether/aether-firewall-helper"
ALLOWED_SERVICES = {"ssh": "22", "mdns": "5353", "http": "80", "https": "443"}


def open_port(port: int, protocol: str) -> dict:
    if protocol not in ("tcp", "udp"):
        return {"ok": False, "error": "protocol must be tcp|udp"}
    if not (1 <= int(port) <= 65535):
        return {"ok": False, "error": "port out of range"}
    try:
        out = subprocess.run(["pkexec", HELPER, "open-port", str(port), protocol],
                             capture_output=True, text=True, timeout=20)
        return {"ok": out.returncode == 0, "error": None if out.returncode == 0 else out.stderr.strip()}
    except FileNotFoundError:
        return {"ok": False, "error": "pkexec not available"}
