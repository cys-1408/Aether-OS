"""Per-application stream listing + volume (real wpctl stream nodes)."""
from __future__ import annotations

import re
import subprocess


def streams() -> dict:
    try:
        out = subprocess.run(["wpctl", "status"], capture_output=True, text=True, timeout=8)
        streams = []
        in_streams = False
        for line in out.stdout.splitlines():
            if "Stream Output:" in line:
                in_streams = True
                continue
            if in_streams and line.strip() and not line.startswith((" ", "\t")):
                in_streams = False
            m = re.match(r"\s*[\* ]?(\d+)\.(\d+\.)?\s+(.+?)\s+\[Vol:", line)
            if m and in_streams:
                streams.append({"id": int(m.group(1)), "app": m.group(3).strip()})
        return {"streams": streams}
    except FileNotFoundError:
        return {"streams": [], "reason": "wpctl not installed"}


def set_stream_volume(node_id: int, percent: int) -> dict:
    percent = max(0, min(150, int(percent)))
    try:
        out = subprocess.run(["wpctl", "set-volume", str(node_id), f"{percent}%"],
                             capture_output=True, text=True, timeout=8)
        return {"ok": out.returncode == 0, "id": node_id, "volume": percent}
    except FileNotFoundError:
        return {"ok": False, "error": "wpctl not installed"}
