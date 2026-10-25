"""Wi-Fi scan helper (library used by the AetherOS network-service).

Wraps ``nmcli -t -f ... dev wifi list`` and returns structured scan results.
Never fabricates networks: an empty list or a scan failure is reported as such.
"""
from __future__ import annotations

import sys
from pathlib import Path

_PKG_DIR = Path(__file__).resolve().parent
if str(_PKG_DIR) not in sys.path:
    sys.path.insert(0, str(_PKG_DIR))

import _nm  # noqa: E402  (shared connection-manager helper module)

WIFI_FIELDS = ("IN-USE", "SSID", "BSSID", "MODE", "CHAN", "FREQ", "SIGNAL", "SECURITY")


class WifiScanError(RuntimeError):
    pass


def _normalize(row: dict) -> dict:
    ssid = row.get("SSID", "")
    hidden = _nm.is_none(ssid) or ssid == "--"
    security = "" if _nm.is_none(row.get("SECURITY", "")) else row["SECURITY"].strip()
    chan_raw = row.get("CHAN", "")
    freq_raw = row.get("FREQ", "").replace(" MHz", "").strip()
    signal_raw = row.get("SIGNAL", "").strip()
    return {
        "ssid": "" if hidden else ssid,
        "hidden": hidden and bool(row.get("BSSID")),
        "bssid": row.get("BSSID", ""),
        "mode": row.get("MODE", ""),
        "channel": int(chan_raw) if chan_raw.strip().isdigit() else None,
        "frequency_mhz": int(freq_raw) if freq_raw.isdigit() else None,
        "signal": int(signal_raw) if signal_raw.isdigit() else None,
        "security": security,
        "secured": bool(security) and security != "--",
        "in_use": row.get("IN-USE", "").strip() == "*",
    }


def scan(*, rescan: bool = True, timeout_s: float = 30.0) -> list[dict]:
    """List visible Wi-Fi networks, optionally forcing a new scan.

    Raises WifiScanError with the stderr text when nmcli fails.
    """
    _nm.require_tool("nmcli", "NetworkManager CLI is required for Wi-Fi scanning")
    argv = ["nmcli", "-t", "-f", ",".join(WIFI_FIELDS), "device", "wifi", "list"]
    if rescan:
        argv += ["--rescan", "yes"]
    else:
        argv += ["--rescan", "no"]
    rc, out, err = _nm.run_text(argv, timeout=timeout_s)
    if rc != 0:
        raise WifiScanError(err.strip() or f"nmcli dev wifi list exited with rc={rc}")
    networks = [_normalize(r) for r in _nm.parse_terse_output(out, WIFI_FIELDS)]
    # dedupe by BSSID, keep strongest signal
    dedup: dict[str, dict] = {}
    for net in networks:
        key = net["bssid"] or net["ssid"] or str(len(dedup))
        prev = dedup.get(key)
        if prev is None or (net["signal"] or 0) > (prev["signal"] or 0):
            dedup[key] = net
    return sorted(dedup.values(), key=lambda n: (not n["in_use"], -(n["signal"] or 0)))
