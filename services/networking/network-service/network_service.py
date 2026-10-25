"""Real NetworkManager integration via nmcli (list argv only)."""
from __future__ import annotations

import re
import subprocess


def _nmcli(argv: list[str], timeout: int = 15) -> subprocess.CompletedProcess:
    return subprocess.run(["nmcli", *argv], capture_output=True, text=True, timeout=timeout)


def general_status() -> dict:
    try:
        out = _nmcli(["-t", "-f", "STATE,CONNECTIVITY,WIFI,WWAN", "general", "status"])
        if out.returncode != 0:
            return {"supported": False, "reason": out.stderr.strip()}
        state, conn, wifi, wwan = (out.stdout.strip().split(":") + [""] * 4)[:4]
        return {"supported": True, "networking": state, "connectivity": conn,
                "wifi_enabled": wifi == "enabled", "wwan_enabled": wwan == "enabled"}
    except FileNotFoundError:
        return {"supported": False, "reason": "nmcli not installed"}
    except subprocess.TimeoutExpired:
        return {"supported": False, "reason": "nmcli timed out"}


def wifi_scan() -> dict:
    try:
        out = _nmcli(["-t", "-f", "SSID,SIGNAL,SECURITY,IN-USE", "dev", "wifi", "list", "--rescan", "yes"], timeout=25)
        if out.returncode != 0:
            return {"networks": [], "reason": out.stderr.strip()}
        networks = []
        for line in out.stdout.splitlines():
            parts = line.split(":")
            if len(parts) >= 4 and parts[0]:
                networks.append({"ssid": parts[0], "signal": parts[1],
                                 "security": parts[2] or "open",
                                 "connected": parts[3] == "*"})
        return {"networks": networks}
    except FileNotFoundError:
        return {"networks": [], "reason": "nmcli not installed"}


def wifi_connect(ssid: str, password: str) -> dict:
    if not ssid or ":" in ssid or "\\n" in ssid:
        return {"ok": False, "error": "invalid ssid"}
    try:
        # password goes via stdin through --ask to keep it out of argv/process list
        proc = subprocess.Popen(
            ["nmcli", "--ask", "dev", "wifi", "connect", ssid],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        out, err = proc.communicate(password + "\n", timeout=45)
        ok = proc.returncode == 0
        return {"ok": ok, "error": None if ok else (err or out).strip() or "connect failed"}
    except (FileNotFoundError, subprocess.TimeoutExpired) as e:
        return {"ok": False, "error": str(e)}


def wifi_disconnect(ssid: str) -> dict:
    try:
        out = _nmcli(["connection", "down", ssid])
        return {"ok": out.returncode == 0, "error": None if out.returncode == 0 else out.stderr.strip()}
    except FileNotFoundError:
        return {"ok": False, "error": "nmcli not installed"}


def enable_networking(enable: bool) -> dict:
    try:
        out = _nmcli(["networking", "on" if enable else "off"])
        return {"ok": out.returncode == 0, "enabled": enable}
    except FileNotFoundError:
        return {"ok": False, "error": "nmcli not installed"}


def set_wifi_enabled(enable: bool) -> dict:
    try:
        out = _nmcli(["radio", "wifi", "on" if enable else "off"])
        return {"ok": out.returncode == 0, "wifi_enabled": enable}
    except FileNotFoundError:
        return {"ok": False, "error": "nmcli not installed"}


def get_dns() -> dict:
    try:
        out = _nmcli(["-t", "-f", "IP4.DNS", "connection", "show", "--active"])
        servers = []
        for line in out.stdout.splitlines():
            dns = line.split(":", 1)[1].strip()
            if dns:
                servers.extend(dns.split(","))
        return {"dns_servers": sorted(set(servers))}
    except FileNotFoundError:
        return {"dns_servers": [], "reason": "nmcli not installed"}


def set_dns(connection: str, servers: list[str]) -> dict:
    for s in servers:
        if not re.fullmatch(r"([0-9]{1,3}(\.[0-9]{1,3}){3}|[0-9a-fA-F:]+)", s):
            return {"ok": False, "error": f"invalid DNS server: {s}"}
    try:
        out = _nmcli(["con", "mod", connection, "ipv4.dns", ",".join(servers),
                      "ipv4.ignore-auto-dns", "yes"])
        ok = out.returncode == 0
        return {"ok": ok, "error": None if ok else out.stderr.strip()}
    except FileNotFoundError:
        return {"ok": False, "error": "nmcli not installed"}


def vpn_status() -> dict:
    try:
        out = _nmcli(["-t", "-f", "NAME,TYPE,DEVICE,STATE", "connection", "show"])
        vpns = []
        for line in out.stdout.splitlines():
            parts = line.split(":")
            if len(parts) == 4 and ("vpn" in parts[1].lower() or "wireguard" in parts[1].lower()):
                vpns.append({"name": parts[0], "type": parts[1], "device": parts[2] or None,
                             "state": parts[3]})
        return {"vpns": vpns}
    except FileNotFoundError:
        return {"vpns": [], "reason": "nmcli not installed"}
