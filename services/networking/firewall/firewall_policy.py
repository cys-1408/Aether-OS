"""Firewall policy via nftables through the polkit helper."""
from __future__ import annotations

import subprocess

HELPER = "/usr/libexec/aether/aether-firewall-helper"
DEFAULT_RULES = "/etc/aether/firewall/default.nft"


def status() -> dict:
    try:
        out = subprocess.run(["nft", "list", "ruleset"], capture_output=True, text=True, timeout=10)
        if out.returncode != 0:
            return {"supported": False, "reason": out.stderr.strip() or "nft unavailable"}
        active = "table inet aether" in out.stdout
        return {"supported": True, "aether_table_active": active, "ruleset_bytes": len(out.stdout)}
    except FileNotFoundError:
        return {"supported": False, "reason": "nft not installed"}


def apply_default() -> dict:
    try:
        out = subprocess.run(["pkexec", HELPER, "apply-default"], capture_output=True, text=True, timeout=20)
        return {"ok": out.returncode == 0, "error": None if out.returncode == 0 else out.stderr.strip()}
    except FileNotFoundError:
        return {"ok": False, "error": "pkexec not available"}


def list_rules() -> dict:
    try:
        out = subprocess.run(["nft", "list", "table", "inet", "aether"], capture_output=True, text=True, timeout=10)
        return {"rules": out.stdout if out.returncode == 0 else None,
                "error": None if out.returncode == 0 else out.stderr.strip()}
    except FileNotFoundError:
        return {"rules": None, "error": "nft not installed"}
