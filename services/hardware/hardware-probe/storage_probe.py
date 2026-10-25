"""Real storage facts via lsblk -J (fallback: /sys/block walk)."""
from __future__ import annotations

import json
import subprocess
from pathlib import Path


def storage_facts() -> list[dict]:
    try:
        out = subprocess.run(
            ["lsblk", "-J", "-o", "NAME,SIZE,TYPE,FSTYPE,MOUNTPOINT,SERIAL,MODEL"],
            capture_output=True, text=True, timeout=5)
        if out.returncode == 0:
            data = json.loads(out.stdout)
            return _flatten(data.get("blockdevices", []))
    except (subprocess.TimeoutExpired, FileNotFoundError, json.JSONDecodeError):
        pass
    # Fallback: /sys/block
    out = []
    for dev in Path("/sys/block").glob("*"):
        if dev.name.startswith(("loop", "ram", "zram")):
            continue
        out.append({"name": dev.name, "size_bytes": None, "fstype": None,
                    "mountpoint": None, "model": None,
                    "health": {"supported": False, "reason": "lsblk unavailable"}})
    return out


def _flatten(nodes: list, depth: int = 0) -> list[dict]:
    out = []
    for n in nodes:
        size = None
        s = n.get("size")
        if isinstance(s, str):
            try:
                size = int(float(s.rstrip("G")) * (1024 ** 3))
            except ValueError:
                size = None
        elif isinstance(s, (int, float)):
            size = int(s)
        out.append({
            "name": n.get("name"), "size_bytes": size, "fstype": n.get("fstype"),
            "mountpoint": n.get("mountpoint"), "model": n.get("model"),
            "type": n.get("type"),
            "health": {"supported": False, "reason": "use SMART via disk-health service"},
        } | ({} if depth else {}))
        children = n.get("children") or []
        if children and depth == 0:
            pass  # keep top-level only for the profile summary
    return out


def smart_health(disk: str) -> dict:
    """SMART via smartctl when installed — truthful unsupported state otherwise."""
    try:
        out = subprocess.run(["smartctl", "-H", "--json", f"/dev/{disk}"],
                             capture_output=True, text=True, timeout=10)
        if out.returncode in (0, 4):
            import json as _json
            data = _json.loads(out.stdout)
            return {"supported": True,
                    "overall": data.get("smart_status", {}).get("overall_pass", None)}
        return {"supported": False, "reason": f"smartctl exit {out.returncode}"}
    except FileNotFoundError:
        return {"supported": False, "reason": "smartctl not installed"}
    except (subprocess.TimeoutExpired, json.JSONDecodeError) as e:
        return {"supported": False, "reason": str(e)}
