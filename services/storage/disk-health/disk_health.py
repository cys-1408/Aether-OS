"""Disk health via smartctl — truthful unsupported reporting."""
from __future__ import annotations

import json
import subprocess


def smart_health(disk: str) -> dict:
    if not disk.replace("_", "").isalnum():
        return {"supported": False, "reason": "invalid disk name"}
    try:
        out = subprocess.run(["smartctl", "-H", "--json", f"/dev/{disk}"],
                             capture_output=True, text=True, timeout=15)
        if out.returncode in (0, 4):  # 4 = healthy with SMART available bits
            data = json.loads(out.stdout)
            status = data.get("smart_status", {})
            return {"supported": True, "disk": disk,
                    "passed": status.get("passed"), "overall": status.get("overall_pass"),
                    "note": "full attributes available via smartctl -a"}
        if out.returncode == 1:
            data = json.loads(out.stdout)
            status = data.get("smart_status", {})
            return {"supported": True, "disk": disk, "passed": status.get("passed", False),
                    "overall": "failing"}
        return {"supported": False, "reason": f"smartctl exit {out.returncode} (no SMART?)"}
    except FileNotFoundError:
        return {"supported": False, "reason": "smartctl not installed"}
    except (subprocess.TimeoutExpired, json.JSONDecodeError) as e:
        return {"supported": False, "reason": str(e)}
