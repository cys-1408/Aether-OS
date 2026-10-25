"""DNS diagnostics for AetherOS.

Reads the per-link DNS configuration from ``resolvectl`` when systemd-resolved
is running, and performs timed lookups using ``dig`` when installed, falling
back to :func:`socket.getaddrinfo`.  All subprocess calls use list argv.
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

_PKG_DIR = Path(__file__).resolve().parent
if str(_PKG_DIR) not in sys.path:
    sys.path.insert(0, str(_PKG_DIR))
_CM_DIR = _PKG_DIR.parent / "connection-manager"
if str(_CM_DIR) not in sys.path:
    sys.path.insert(0, str(_CM_DIR))

import _nm  # noqa: E402
from dns_configuration import resolvectl_status  # noqa: E402


def resolver_config() -> dict:
    """Return the resolvectl link view (None fields when unavailable)."""
    status = resolvectl_status()
    if status is None:
        return {
            "systemd_resolved": False,
            "reason": "resolvectl not installed or systemd-resolved not running",
        }
    return {"systemd_resolved": True, "links": status.get("links", {}),
            "global_dns_servers": status.get("global_dns_servers", [])}


def resolve(host: str, *, timeout_s: float = 5.0) -> dict:
    """Resolve ``host`` with dig when available, else getaddrinfo; timed."""
    if not host or not isinstance(host, str):
        return {"ok": False, "resolver": None, "addresses": [], "error": "host must be a non-empty string"}
    if _nm.tool_path("dig") is not None:
        started = time.monotonic()
        rc, out, err = _nm.run_text(
            ["dig", "+time=" + str(max(1, int(timeout_s))), "+tries=1", "+short", host],
            timeout=timeout_s + 2.0,
        )
        elapsed_ms = (time.monotonic() - started) * 1000.0
        addresses = [line.strip() for line in out.splitlines() if line.strip()]
        if rc == 0 and addresses:
            return {"ok": True, "resolver": "dig", "addresses": addresses,
                    "elapsed_ms": round(elapsed_ms, 1), "error": None}
        if rc != 0:
            return {"ok": False, "resolver": "dig", "addresses": [],
                    "elapsed_ms": round(elapsed_ms, 1),
                    "error": err.strip() or f"dig exited rc={rc}"}
        # dig rc==0 with no answer: NXDOMAIN-ish; fall through to getaddrinfo
    import socket
    started = time.monotonic()
    try:
        infos = socket.getaddrinfo(host, 443, proto=socket.IPPROTO_TCP)
        addresses = []
        for info in infos:
            if info[4][0] not in addresses:
                addresses.append(info[4][0])
        elapsed_ms = (time.monotonic() - started) * 1000.0
        return {"ok": bool(addresses), "resolver": "getaddrinfo", "addresses": addresses,
                "elapsed_ms": round(elapsed_ms, 1), "error": None if addresses else "no addresses"}
    except OSError as exc:
        elapsed_ms = (time.monotonic() - started) * 1000.0
        return {"ok": False, "resolver": "getaddrinfo", "addresses": [],
                "elapsed_ms": round(elapsed_ms, 1), "error": str(exc)}


def dns_report(hosts: list[str] | None = None, *, timeout_s: float = 5.0) -> dict:
    """Full DNS diagnostic: resolver config + timed lookups for each host."""
    targets = hosts or ["dns.google", "archlinux.org"]
    return {
        "resolver_config": resolver_config(),
        "lookups": [resolve(h, timeout_s=timeout_s) for h in targets],
    }
