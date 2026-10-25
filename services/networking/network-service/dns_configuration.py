"""DNS get/set for the AetherOS network-service (nmcli connection properties).

``Network.get_dns`` / ``Network.set_dns`` land here.  DNS servers are
validated with :mod:`ipaddress`; nmcli property values are passed as a single
argv element (never through a shell).  The resolv.conf/systemd-resolved view
comes from the shared connection-manager library, imported under a distinct
module name because the service ships a module with the same file name.
"""
from __future__ import annotations

import importlib.util
import ipaddress
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
_CM_DIR = REPO_ROOT / "networking" / "connection-manager"
if str(_CM_DIR) not in sys.path:
    sys.path.insert(0, str(_CM_DIR))

import _nm  # noqa: E402

_spec = importlib.util.spec_from_file_location(
    "aether_cm_dns_configuration", _CM_DIR / "dns_configuration.py")
assert _spec and _spec.loader, "connection-manager dns_configuration.py missing"
_cm_dns = importlib.util.module_from_spec(_spec)
sys.modules.setdefault("aether_cm_dns_configuration", _cm_dns)
_spec.loader.exec_module(_cm_dns)

from connection_state import active_connections  # noqa: E402

_DNS_FIELDS = ("ipv4.dns", "ipv6.dns", "ipv4.dns-search")


class DnsError(RuntimeError):
    pass


def _validate_servers(dns: list) -> tuple[list[str], list[str]]:
    v4: list[str] = []
    v6: list[str] = []
    for server in dns:
        if not isinstance(server, str):
            raise DnsError("dns entries must be strings")
        try:
            addr = ipaddress.ip_address(server.strip())
        except ValueError as exc:
            raise DnsError(f"invalid DNS server {server!r}") from exc
        (v4 if addr.version == 4 else v6).append(str(addr))
    return v4, v6


def _connection_dns(name: str, timeout_s: float = 10.0) -> dict:
    rc, out, err = _nm.run_text(
        ["nmcli", "-t", "-f", ",".join(_DNS_FIELDS), "con", "show", name],
        timeout=timeout_s,
    )
    if rc != 0:
        raise DnsError(err.strip() or f"nmcli con show {name!r} failed rc={rc}")
    row = _nm.parse_terse_output(out, _DNS_FIELDS)
    if not row:
        return {"ipv4": [], "ipv6": [], "search": []}
    r = row[0]
    split = lambda v: [s for s in (v or "").split() if s]  # noqa: E731
    return {"ipv4": split(r.get("ipv4.dns")),
            "ipv6": split(r.get("ipv6.dns")),
            "search": split(r.get("ipv4.dns-search"))}


def get_dns(connection: str | None = None, *, timeout_s: float = 10.0) -> dict:
    """DNS servers of one connection (default: every active connection)."""
    _nm.require_tool("nmcli", "NetworkManager CLI is required")
    names = [connection] if connection else [c["name"] for c in active_connections(timeout_s)]
    connections: list[dict] = []
    errors: list[str] = []
    for name in names:
        if not name:
            continue
        try:
            connections.append({"name": name, "dns": _connection_dns(name, timeout_s)})
        except DnsError as exc:
            errors.append(str(exc))
    result: dict = {
        "connections": connections,
        "resolv_conf": _cm_dns.parse_resolv_conf(),
        "systemd_resolved": _cm_dns.resolvectl_status(),
        "errors": errors,
    }
    return result


def set_dns(connection: str, dns: list | None = None, *, reset: bool = False,
            apply: bool = False, timeout_s: float = 15.0) -> dict:
    """Set (or clear with ``reset=True``) the DNS servers of a connection."""
    _nm.require_tool("nmcli", "NetworkManager CLI is required")
    if not isinstance(connection, str) or not connection.strip():
        raise DnsError("connection name is required")
    connection = connection.strip()
    dns = dns or []
    if reset and dns:
        raise DnsError("pass either dns=[...] or reset=True, not both")
    v4, v6 = _validate_servers(dns)

    rc, out, err = _nm.run_text(
        ["nmcli", "-t", "-f", "NAME", "con", "show"], timeout=timeout_s)
    if rc != 0:
        raise DnsError(err.strip() or "nmcli con show failed")
    known = [row["NAME"] for row in _nm.parse_terse_output(out, ("NAME",))]
    if connection not in known:
        raise DnsError(f"connection {connection!r} does not exist")

    changes: list[str] = []
    argv_v4 = ["nmcli", "con", "mod", connection, "ipv4.dns",
               "" if reset else _nm.format_dns_list(v4)]
    rc, _out, err = _nm.run_text(argv_v4, timeout=timeout_s)
    if rc != 0:
        raise DnsError(err.strip() or "nmcli con mod ipv4.dns failed")
    changes.append("ipv4.dns")

    if v6 or reset:
        rc, _out, err = _nm.run_text(
            ["nmcli", "con", "mod", connection, "ipv6.dns",
             "" if reset else _nm.format_dns_list(v6)], timeout=timeout_s)
        if rc != 0:
            raise DnsError(err.strip() or "nmcli con mod ipv6.dns failed")
        changes.append("ipv6.dns")

    reactivated = False
    if apply:
        rc, _out, err = _nm.run_text(["nmcli", "con", "up", connection], timeout=timeout_s + 45.0)
        if rc != 0:
            raise DnsError(err.strip() or f"nmcli con up {connection!r} failed")
        reactivated = True

    return {
        "connection": connection,
        "ipv4_dns": v4,
        "ipv6_dns": v6,
        "reset": reset,
        "changed_fields": changes,
        "reactivated": reactivated,
    }
