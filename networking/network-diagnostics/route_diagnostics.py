"""Route diagnostics for AetherOS.

Parses ``ip route show`` / ``ip -6 route show`` output and cross-references
interface state from sysfs.  Real kernel data only.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

_PKG_DIR = Path(__file__).resolve().parent
if str(_PKG_DIR) not in sys.path:
    sys.path.insert(0, str(_PKG_DIR))
_CM_DIR = _PKG_DIR.parent / "connection-manager"
if str(_CM_DIR) not in sys.path:
    sys.path.insert(0, str(_CM_DIR))

import _nm  # noqa: E402

SYSFS_NET = Path("/sys/class/net")


def parse_route_line(line: str, family: str) -> dict:
    """Parse one ``ip route`` line into a structured entry."""
    parts = line.split()
    entry: dict = {"family": family, "raw": line, "destination": None, "via": None,
                   "dev": None, "protocol": None, "metric": None, "scope": None}
    if not parts:
        return entry
    if parts[0] == "default":
        entry["destination"] = "default"
        iterator = parts[1:]
    else:
        entry["destination"] = parts[0]
        iterator = parts[1:]
    key_map = {"via": "via", "dev": "dev", "proto": "protocol", "metric": "metric", "scope": "scope"}
    i = 0
    while i < len(iterator):
        token = iterator[i]
        if token in key_map and i + 1 < len(iterator):
            entry[key_map[token]] = iterator[i + 1]
            i += 2
        else:
            i += 1
    return entry


def routes(family: str = "4", timeout_s: float = 10.0) -> list[dict]:
    """Return parsed routes for family '4' or '6' (ip binary required)."""
    if _nm.tool_path("ip") is None:
        raise _nm.ToolNotFound("ip", "iproute2 is required for route diagnostics")
    argv = ["ip", "-6", "route", "show"] if family == "6" else ["ip", "route", "show"]
    rc, out, err = _nm.run_text(argv, timeout=timeout_s)
    if rc != 0:
        raise RuntimeError(err.strip() or f"ip route show exited rc={rc}")
    return [parse_route_line(line, family) for line in out.splitlines() if line.strip()]


def interfaces() -> list[dict]:
    """Interface summary from sysfs."""
    out: list[dict] = []
    if not SYSFS_NET.is_dir():
        return out
    for name in sorted(os.listdir(SYSFS_NET)):
        base = SYSFS_NET / name
        def _read(field: str) -> str | None:
            try:
                return (base / field).read_text(errors="replace").strip()
            except OSError:
                return None
        out.append({
            "name": name,
            "operstate": _read("operstate") or "unknown",
            "mtu": _read("mtu"),
            "mac_address": _read("address"),
        })
    return out


def route_report() -> dict:
    """Combined IPv4/IPv6 route + interface report (honest on failure)."""
    report: dict = {"interfaces": interfaces(), "routes": [], "errors": []}
    for family in ("4", "6"):
        try:
            report["routes"].extend(routes(family))
        except _nm.ToolNotFound as exc:
            report["errors"].append(str(exc))
            break
        except RuntimeError as exc:
            report["errors"].append(f"ipv{family}: {exc}")
    report["default_route"] = next(
        (r for r in report["routes"] if r["destination"] == "default" and r["family"] == "4"),
        None,
    )
    return report
