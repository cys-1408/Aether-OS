"""Real network interface facts from /sys/class/net."""
from __future__ import annotations

from pathlib import Path


def network_facts() -> list[dict]:
    out = []
    base = Path("/sys/class/net")
    try:
        ifaces = sorted(base.iterdir())
    except OSError:
        ifaces = []
    for iface in ifaces:
        name = iface.name
        kind = "loopback" if name == "lo" else "ethernet"
        try:
            if (iface / "wireless").exists() or (iface / "phy80211").exists():
                kind = "wifi"
        except OSError:
            pass
        state = None
        try:
            state = (iface / "operstate").read_text().strip()
        except OSError:
            pass
        mac = None
        try:
            mac = (iface / "address").read_text().strip()
        except OSError:
            pass
        out.append({"name": name, "state": state, "kind": kind, "mac": mac})
    return out
