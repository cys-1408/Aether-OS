"""Real connectivity checks for AetherOS diagnostics.

Per probe: DNS resolution via ``socket.getaddrinfo`` followed by an HTTP HEAD
request (urllib, strict timeout, no shell, no third-party deps).  A probe host
that answers with any HTTP status (even 403/405) proves TCP + TLS + HTTP
reachability; that is reported truthfully instead of guessing.
"""
from __future__ import annotations

import datetime as _dt
import socket
import time
import urllib.error
import urllib.request

DEFAULT_PROBE_HOSTS = ("connectivity-check.archlinux.org", "dns.google")
DEFAULT_TIMEOUT_S = 5.0


def resolve_host(host: str, timeout_s: float = DEFAULT_TIMEOUT_S) -> tuple[bool, list[str], str | None]:
    """Resolve ``host``; returns (ok, addresses, error)."""
    try:
        infos = socket.getaddrinfo(host, 443, proto=socket.IPPROTO_TCP)
    except socket.gaierror as exc:
        return False, [], f"DNS resolution failed: {exc}"
    except OSError as exc:
        return False, [], f"resolver error: {exc}"
    addresses: list[str] = []
    for info in infos:
        addr = info[4][0]
        if addr not in addresses:
            addresses.append(addr)
    return bool(addresses), addresses, None


def http_probe(host: str, *, timeout_s: float = DEFAULT_TIMEOUT_S,
               url: str | None = None) -> dict:
    """HTTP HEAD probe against ``host`` (or full ``url``)."""
    target = url or f"https://{host}/"
    started = time.monotonic()
    try:
        req = urllib.request.Request(target, method="HEAD",
                                     headers={"User-Agent": "aetheros-connectivity/1.0"})
        with urllib.request.urlopen(req, timeout=timeout_s) as resp:
            elapsed_ms = (time.monotonic() - started) * 1000.0
            return {
                "host": host,
                "url": target,
                "ok": True,
                "status_code": resp.status,
                "latency_ms": round(elapsed_ms, 1),
                "error": None,
            }
    except urllib.error.HTTPError as exc:
        elapsed_ms = (time.monotonic() - started) * 1000.0
        # An HTTP error still proves the network path (TCP/TLS/HTTP) works.
        return {
            "host": host, "url": target, "ok": True, "status_code": exc.code,
            "latency_ms": round(elapsed_ms, 1), "error": f"http status {exc.code}",
        }
    except (urllib.error.URLError, OSError, ValueError) as exc:
        elapsed_ms = (time.monotonic() - started) * 1000.0
        return {
            "host": host, "url": target, "ok": False, "status_code": None,
            "latency_ms": round(elapsed_ms, 1), "error": str(exc),
        }


def check_connectivity(hosts: list[str] | tuple[str, ...] | None = None,
                       *, timeout_s: float = DEFAULT_TIMEOUT_S) -> dict:
    """Run DNS + HTTP probes and return an honest overall verdict."""
    probe_hosts = tuple(hosts) if hosts else DEFAULT_PROBE_HOSTS
    checks: list[dict] = []
    for host in probe_hosts:
        dns_ok, addresses, dns_error = resolve_host(host, timeout_s)
        entry: dict = {
            "host": host,
            "dns_ok": dns_ok,
            "resolved_ips": addresses,
            "dns_error": dns_error,
        }
        if dns_ok:
            entry.update(http_probe(host, timeout_s=timeout_s))
        else:
            entry.update({"ok": False, "status_code": None, "latency_ms": None})
        checks.append(entry)
    return {
        "online": any(c.get("ok") for c in checks),
        "checks": checks,
        "checked_at": _dt.datetime.now(_dt.timezone.utc).isoformat(),
        "probe_hosts": list(probe_hosts),
    }
