"""NTP sync status via timedatectl (real state)."""
from __future__ import annotations

import subprocess


def sync_status() -> dict:
    try:
        out = subprocess.run(["timedatectl", "show", "-p", "NTP", "-p", "NTPSynchronized"],
                             capture_output=True, text=True, timeout=5)
        props = dict(line.split("=", 1) for line in out.stdout.splitlines() if "=" in line)
        return {"ntp_enabled": props.get("NTP"), "synchronized": props.get("NTPSynchronized")}
    except FileNotFoundError:
        return {"reason": "timedatectl not installed"}


def enable_ntp(enable: bool) -> dict:
    try:
        subprocess.run(["timedatectl", "set-ntp", "true" if enable else "false"],
                       check=True, timeout=15)
        return {"ok": True, "ntp": enable}
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError) as e:
        return {"ok": False, "error": str(e)}
