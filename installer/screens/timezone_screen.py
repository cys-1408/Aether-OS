"""Timezone choice via timedatectl list."""
from __future__ import annotations

import subprocess


def zones() -> list[str]:
    try:
        out = subprocess.run(["timedatectl", "list-timezones"], capture_output=True, text=True, timeout=10)
        return [z.strip() for z in out.stdout.splitlines() if z.strip()]
    except FileNotFoundError:
        return ["UTC"]


def ask_cli() -> str:
    cur = "UTC"
    tz = input(f"Timezone [{cur}]: ").strip() or cur
    return tz if tz in zones() else cur
