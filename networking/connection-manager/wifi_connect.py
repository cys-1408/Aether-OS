"""Wi-Fi connect helper (library used by the AetherOS network-service).

Secrets never appear in the process argument vector: when a password is
supplied, ``nmcli --ask`` is used and the secret is written to nmcli's stdin
pipe.  All invocations use list argv and bounded timeouts.
"""
from __future__ import annotations

import sys
from pathlib import Path

_PKG_DIR = Path(__file__).resolve().parent
if str(_PKG_DIR) not in sys.path:
    sys.path.insert(0, str(_PKG_DIR))

import _nm  # noqa: E402  (shared connection-manager helper module)
from wifi_scan import scan  # noqa: E402


class WifiConnectError(RuntimeError):
    pass


def _active_wifi_connection() -> dict | None:
    rc, out, _ = _nm.run_text(
        ["nmcli", "-t", "-f", "NAME,UUID,TYPE,DEVICE,STATE", "con", "show", "--active"],
        timeout=10.0,
    )
    if rc != 0:
        return None
    for row in _nm.parse_terse_output(out, ("NAME", "UUID", "TYPE", "DEVICE", "STATE")):
        if row.get("TYPE", "").startswith("802-11-wireless") and row.get("STATE") == "activated":
            return row
    return None


def _first_wifi_device() -> str | None:
    rc, out, _ = _nm.run_text(
        ["nmcli", "-t", "-f", "DEVICE,TYPE,STATE,CONNECTION", "device", "status"],
        timeout=10.0,
    )
    if rc != 0:
        return None
    for row in _nm.parse_terse_output(out, ("DEVICE", "TYPE", "STATE", "CONNECTION")):
        if row.get("TYPE", "") == "wifi" and row.get("DEVICE") not in ("", "--"):
            return row["DEVICE"]
    return None


def connect(ssid: str, *, password: str | None = None, hidden: bool = False,
            timeout_s: float = 60.0) -> dict:
    """Connect to ``ssid``; feed the password through stdin (never argv).

    Returns a dict describing the activated connection. Raises
    WifiConnectError when nmcli fails or when a secured network is targeted
    without a password.
    """
    if not isinstance(ssid, str) or not ssid.strip():
        raise ValueError("ssid must be a non-empty string")
    if len(ssid) > 32:
        raise ValueError("ssid longer than 32 bytes is not a valid SSID")
    _nm.require_tool("nmcli", "NetworkManager CLI is required for Wi-Fi connect")

    if password is None:
        secured = [n for n in scan(rescan=False, timeout_s=min(timeout_s, 30.0))
                   if n["ssid"] == ssid and n["secured"]]
        if secured:
            raise WifiConnectError(
                f"network '{ssid}' is secured (WPA/WPA3/802.1X) but no password was supplied")

    argv = ["nmcli", "--ask", "device", "wifi", "connect", ssid]
    if hidden:
        argv += ["hidden", "yes"]
    input_bytes = (password + "\n").encode("utf-8") if password is not None else None
    rc, out, err = _nm.run_text(argv, timeout=timeout_s, input_bytes=input_bytes)
    if rc != 0:
        raise WifiConnectError(err.strip() or out.strip() or f"nmcli exited with rc={rc}")
    active = _active_wifi_connection()
    return {
        "connected": active is not None,
        "ssid": ssid,
        "connection": active["NAME"] if active else None,
        "device": active["DEVICE"] if active else None,
        "uuid": active["UUID"] if active else None,
        "state": active["STATE"] if active else "activating",
    }


def disconnect(device: str | None = None, *, timeout_s: float = 15.0) -> dict:
    """Disconnect a Wi-Fi device (defaults to the first Wi-Fi device)."""
    _nm.require_tool("nmcli", "NetworkManager CLI is required for Wi-Fi disconnect")
    target = device or _first_wifi_device()
    if not target:
        raise WifiConnectError("no Wi-Fi device found")
    rc, _out, err = _nm.run_text(["nmcli", "device", "disconnect", target], timeout=timeout_s)
    if rc != 0:
        raise WifiConnectError(err.strip() or f"nmcli device disconnect exited with rc={rc}")
    return {"disconnected": True, "device": target}
