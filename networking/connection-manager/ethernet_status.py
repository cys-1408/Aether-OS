"""Wired Ethernet status helper.

Reads real kernel state from sysfs (``/sys/class/net``) and merges the
NetworkManager view via ``nmcli -t device status``.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

_PKG_DIR = Path(__file__).resolve().parent
if str(_PKG_DIR) not in sys.path:
    sys.path.insert(0, str(_PKG_DIR))

import _nm  # noqa: E402  (shared connection-manager helper module)

SYSFS_NET = Path("/sys/class/net")


def _read_sysfs(path: Path) -> str | None:
    try:
        return path.read_text(encoding="utf-8", errors="replace").strip()
    except (OSError, ValueError):
        return None


def _is_ethernet(name: str) -> bool:
    # /sys/class/net/<dev>/type == 1 means Ethernet (ARPHRD_ETHER).
    dev_type = _read_sysfs(SYSFS_NET / name / "type")
    return dev_type == "1" and not name.startswith(("lo", "virbr", "docker", "veth", "br-"))


def _sysfs_device(name: str) -> dict:
    base = SYSFS_NET / name
    speed_raw = _read_sysfs(base / "speed")
    carrier_raw = _read_sysfs(base / "carrier")
    try:
        carrier = int(carrier_raw) == 1
    except (TypeError, ValueError):
        carrier = None  # e.g. "Invalid argument" when the link is down
    return {
        "device": name,
        "operstate": _read_sysfs(base / "operstate") or "unknown",
        "carrier": carrier,
        "speed_mbps": int(speed_raw) if speed_raw and speed_raw.isdigit() else None,
        "duplex": _read_sysfs(base / "duplex"),
        "mtu": int(m) if (m := _read_sysfs(base / "mtu")) and m.isdigit() else None,
        "mac_address": _read_sysfs(base / "address"),
    }


def wired_devices() -> list[dict]:
    """Return one dict per physical Ethernet device known to the kernel."""
    if not SYSFS_NET.is_dir():
        return []
    devices = [_sysfs_device(name) for name in sorted(os.listdir(SYSFS_NET)) if _is_ethernet(name)]
    if _nm.nmcli_available():
        rc, out, _ = _nm.run_text(
            ["nmcli", "-t", "-f", "DEVICE,TYPE,STATE,CONNECTION", "device", "status"],
            timeout=10.0,
        )
        by_name: dict[str, dict] = {}
        if rc == 0:
            for row in _nm.parse_terse_output(out, ("DEVICE", "TYPE", "STATE", "CONNECTION")):
                if row.get("TYPE") == "ethernet":
                    by_name[row["DEVICE"]] = row
        for dev in devices:
            nm = by_name.get(dev["device"])
            if nm:
                dev["nm_state"] = nm.get("STATE")
                dev["connection"] = None if _nm.is_none(nm.get("CONNECTION", "")) else nm["CONNECTION"]
            else:
                dev["nm_state"] = "unmanaged"
                dev["connection"] = None
    else:
        for dev in devices:
            dev["nm_state"] = "nmcli-missing"
            dev["connection"] = None
    return devices
