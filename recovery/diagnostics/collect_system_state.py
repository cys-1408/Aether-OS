"""Redacted diagnostics collection in recovery."""
from __future__ import annotations

import subprocess


def collect() -> dict:
    def run(argv, timeout=20):
        try:
            return subprocess.run(argv, capture_output=True, text=True, timeout=timeout).stdout[-600:]
        except (FileNotFoundError, subprocess.TimeoutExpired) as e:
            return f"unavailable: {e}"
    return {"lsblk": run(["lsblk", "-J"]), "failed": run(["systemctl", "--failed", "--no-pager"]),
            "journal_err": run(["journalctl", "-p", "err", "-n", "50", "--no-pager"])}
