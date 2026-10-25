"""Clock + timezone via timedatectl; locale-aware formatting."""
from __future__ import annotations

import subprocess
import time
from datetime import datetime
from zoneinfo import ZoneInfo


def now(zone: str | None = None) -> dict:
    tz = ZoneInfo(zone) if zone else datetime.now().astimezone().tzinfo
    dt = datetime.now(tz)
    return {"iso": dt.isoformat(timespec="seconds"), "epoch": int(time.time()),
            "timezone": str(tz), "utc_offset": dt.strftime("%z")}


def timezone_info() -> dict:
    try:
        out = subprocess.run(["timedatectl", "show"], capture_output=True, text=True, timeout=5)
        props = dict(line.split("=", 1) for line in out.stdout.splitlines() if "=" in line)
        return {"timezone": props.get("Timezone", "UTC"), "ntp": props.get("NTP"),
                "synchronized": props.get("NTPSynchronized")}
    except FileNotFoundError:
        return {"timezone": time.tzname[0], "ntp": None}


def set_timezone(tz: str) -> dict:
    try:
        subprocess.run(["timedatectl", "set-timezone", tz], check=True, timeout=15)
        return {"ok": True, "timezone": tz}
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError) as e:
        return {"ok": False, "error": str(e)}


def locales() -> dict:
    try:
        out = subprocess.run(["locale"], capture_output=True, text=True, timeout=5)
        vals = dict(line.split("=", 1) for line in out.stdout.splitlines() if "=" in line)
        return {"lang": vals.get("LANG"), "lc_time": vals.get("LC_TIME")}
    except FileNotFoundError:
        return {"lang": None}


def format_local(dt: datetime | None = None, zone: str | None = None) -> str:
    tz = ZoneInfo(zone) if zone else None
    value = dt or datetime.now(tz)
    return value.strftime("%A, %d %B %Y %H:%M:%S %Z")
