"""Wi-Fi adapter state."""
from __future__ import annotations

import subprocess


def adapter_state() -> dict:
    try:
        out = subprocess.run(["nmcli", "-t", "-f", "DEVICE,TYPE,STATE,CONNECTION", "device", "status"],
                             capture_output=True, text=True, timeout=10)
        wifi = []
        for line in out.stdout.splitlines():
            parts = line.split(":")
            if len(parts) == 4 and parts[1] == "wifi":
                wifi.append({"device": parts[0], "state": parts[2], "connection": parts[3] or None})
        return {"adapters": wifi}
    except FileNotFoundError:
        return {"adapters": [], "reason": "nmcli not installed"}
