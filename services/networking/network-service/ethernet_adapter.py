"""Ethernet adapter state."""
from __future__ import annotations

import subprocess


def ethernet_state() -> dict:
    try:
        out = subprocess.run(["nmcli", "-t", "-f", "DEVICE,TYPE,STATE,CONNECTION", "device", "status"],
                             capture_output=True, text=True, timeout=10)
        eth = []
        for line in out.stdout.splitlines():
            parts = line.split(":")
            if len(parts) == 4 and parts[1] in ("ethernet", "bridge"):
                eth.append({"device": parts[0], "state": parts[2], "connection": parts[3] or None})
        return {"adapters": eth}
    except FileNotFoundError:
        return {"adapters": [], "reason": "nmcli not installed"}
