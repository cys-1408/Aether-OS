"""DNS configuration helper (library layer shared across AetherOS networking tools).

Parses ``/etc/resolv.conf`` and, when available, the per-link view of
``resolvectl``; validates DNS server addresses with :mod:`ipaddress`.
"""
from __future__ import annotations

import ipaddress
import sys
from pathlib import Path

_PKG_DIR = Path(__file__).resolve().parent
if str(_PKG_DIR) not in sys.path:
    sys.path.insert(0, str(_PKG_DIR))

import _nm  # noqa: E402  (shared connection-manager helper module)

DEFAULT_RESOLV_CONF = Path("/etc/resolv.conf")


def valid_dns_server(value: str) -> bool:
    try:
        ipaddress.ip_address(value.strip())
        return True
    except (ValueError, AttributeError):
        return False


def parse_resolv_conf(path: Path | str = DEFAULT_RESOLV_CONF) -> dict:
    """Parse a resolv.conf into nameservers / search / options lists."""
    res: dict = {"nameservers": [], "search": [], "options": [], "path": str(path)}
    try:
        text = Path(path).read_text(encoding="utf-8", errors="replace")
    except OSError as exc:
        res["error"] = f"cannot read {path}: {exc.strerror or exc}"
        return res
    for raw in text.splitlines():
        line = raw.split("#", 1)[0].strip()
        if not line:
            continue
        parts = line.split()
        if not parts:
            continue
        if parts[0] == "nameserver" and len(parts) >= 2:
            res["nameservers"].append(parts[1])
        elif parts[0] == "search":
            res["search"].extend(parts[1:])
        elif parts[0] == "domain" and len(parts) >= 2:
            res["search"].append(parts[1])
        elif parts[0] == "options":
            res["options"].extend(parts[1:])
    res["nameservers"] = [ns for ns in res["nameservers"] if valid_dns_server(ns)]
    return res


def resolvectl_status(timeout_s: float = 10.0) -> dict | None:
    """Return a light parse of ``resolvectl status`` or None if unavailable."""
    if _nm.tool_path("resolvectl") is None:
        return None
    rc, out, _err = _nm.run_text(["resolvectl", "status"], timeout=timeout_s)
    if rc != 0:
        return None
    result: dict = {"global_dns_servers": [], "links": {}}
    current_link = "__global__"
    link_servers: list[str] = []
    for raw in out.splitlines():
        line = raw.rstrip()
        stripped = line.strip()
        link_marker = stripped.startswith("Link ")
        if link_marker:
            if link_servers and current_link != "__global__":
                result["links"][current_link]["dns_servers"] = list(link_servers)
            parts = stripped.split("(", 1)
            current_link = parts[0][len("Link "):].strip()
            result["links"].setdefault(current_link, {})
            link_servers = []
            continue
        if stripped.startswith("DNS Servers:"):
            servers = stripped[len("DNS Servers:"):].split()
            if line.startswith(("       ", "\t")) or current_link == "__global__":
                link_servers.extend(servers)
        elif stripped.startswith("Current DNS Server:"):
            server = stripped[len("Current DNS Server:"):].strip()
            if current_link == "__global__":
                result["global_dns_servers"].append(server)
    if link_servers and current_link != "__global__":
        result["links"].setdefault(current_link, {})["dns_servers"] = list(link_servers)
    return result


def current_dns(resolv_conf_path: Path | str = DEFAULT_RESOLV_CONF) -> dict:
    """Best-effort summary of the effective DNS configuration."""
    summary: dict = {
        "resolv_conf": parse_resolv_conf(resolv_conf_path),
        "systemd_resolved": resolvectl_status(),
    }
    summary["valid_nameservers"] = [
        ns for ns in summary["resolv_conf"].get("nameservers", []) if valid_dns_server(ns)
    ]
    return summary
