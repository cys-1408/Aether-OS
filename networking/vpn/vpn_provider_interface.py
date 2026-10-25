"""VPN status library for AetherOS (NetworkManager-backed).

Reads VPN tunnels known to NetworkManager: classic ``vpn`` connections
(OpenVPN, strongSwan, WireGuard plugin, ...) and native ``wireguard``
interfaces. Reports only what nmcli actually says.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

_PKG_DIR = Path(__file__).resolve().parent
if str(_PKG_DIR) not in sys.path:
    sys.path.insert(0, str(_PKG_DIR))
_CM_DIR = _PKG_DIR.parent / "connection-manager"
if str(_CM_DIR) not in sys.path:
    sys.path.insert(0, str(_CM_DIR))

import _nm  # noqa: E402  (shared connection-manager helper module)

VPN_TYPES = ("vpn", "wireguard")
PROVIDER_SERVICE_TYPES = {
    "org.freedesktop.NetworkManager.openvpn": "openvpn",
    "org.freedesktop.NetworkManager.strongswan": "strongswan",
    "org.freedesktop.NetworkManager.openswan": "openswan",
    "org.freedesktop.NetworkManager.l2tp": "l2tp",
    "org.freedesktop.NetworkManager.pptp": "pptp",
    "org.freedesktop.NetworkManager.vpnc": "vpnc",
    "org.freedesktop.NetworkManager.wireguard": "wireguard",
    "org.freedesktop.NetworkManager.ssh": "ssh",
}

_CON_FIELDS = ("NAME", "UUID", "TYPE", "DEVICE", "STATE")


def _connections(timeout_s: float = 10.0, active_only: bool = False) -> list[dict]:
    argv = ["nmcli", "-t", "-f", ",".join(_CON_FIELDS), "con", "show"]
    if active_only:
        argv.append("--active")
    rc, out, err = _nm.run_text(argv, timeout=timeout_s)
    if rc != 0:
        raise _nm.ToolNotFound("nmcli", err.strip() or "nmcli con show failed")
    rows = _nm.parse_terse_output(out, _CON_FIELDS)
    return [r for r in rows if r.get("TYPE", "").split("-")[-1] in VPN_TYPES
            or r.get("TYPE") in VPN_TYPES]


class VpnProviderInterface:
    """Provider-agnostic view over NM VPN connections."""

    def list_connections(self, timeout_s: float = 10.0) -> list[dict]:
        out: list[dict] = []
        for row in _connections(timeout_s):
            out.append({
                "name": row["NAME"],
                "uuid": row["UUID"],
                "type": row["TYPE"],
                "device": None if _nm.is_none(row.get("DEVICE", "")) else row["DEVICE"],
                "state": row["STATE"],
                "active": row.get("STATE") == "activated",
            })
        return out

    def provider_of(self, name: str, timeout_s: float = 10.0) -> str | None:
        rc, out, _err = _nm.run_text(
            ["nmcli", "-t", "-f", "vpn.service-type,connection.type", "con", "show", name],
            timeout=timeout_s,
        )
        if rc != 0:
            return None
        for row in _nm.parse_terse_output(out, ("vpn.service-type", "connection.type")):
            service = row.get("vpn.service-type", "")
            if service in PROVIDER_SERVICE_TYPES:
                return PROVIDER_SERVICE_TYPES[service]
        return "wireguard" if rc == 0 else None

    def connect(self, name: str, timeout_s: float = 60.0) -> dict:
        _nm.require_tool("nmcli", "NetworkManager CLI is required")
        rc, _out, err = _nm.run_text(["nmcli", "con", "up", name], timeout=timeout_s)
        if rc != 0:
            raise RuntimeError(err.strip() or f"nmcli con up {name!r} failed rc={rc}")
        return {"name": name, "state": "activated"}

    def disconnect(self, name: str, timeout_s: float = 30.0) -> dict:
        _nm.require_tool("nmcli", "NetworkManager CLI is required")
        rc, _out, err = _nm.run_text(["nmcli", "con", "down", name], timeout=timeout_s)
        if rc != 0:
            raise RuntimeError(err.strip() or f"nmcli con down {name!r} failed rc={rc}")
        return {"name": name, "state": "deactivated"}


def vpn_status(timeout_s: float = 15.0) -> dict:
    """Summarize the current VPN situation truthfully."""
    if not _nm.nmcli_available():
        return {
            "supported": False,
            "reason": "nmcli (NetworkManager) not installed",
            "active": [],
            "configured": [],
        }
    try:
        all_conns = _connections(timeout_s, active_only=False)
        active = [c for c in all_conns if c.get("STATE") == "activated"]
    except _nm.ToolNotFound as exc:
        return {"supported": False, "reason": str(exc), "active": [], "configured": []}
    interface = VpnProviderInterface()
    configured = []
    providers: set[str] = set()
    for conn in all_conns:
        provider = interface.provider_of(conn["NAME"], timeout_s)
        if provider:
            providers.add(provider)
        configured.append({
            "name": conn["NAME"],
            "type": conn["TYPE"],
            "provider": provider,
            "active": conn.get("STATE") == "activated",
        })
    return {
        "supported": True,
        "backend": "networkmanager",
        "providers_detected": sorted(providers),
        "configured": configured,
        "active": [c["NAME"] for c in active],
        "count_configured": len(configured),
        "count_active": len(active),
    }
