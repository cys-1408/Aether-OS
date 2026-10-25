"""DMI/firmware identity from /sys/class/dmi/id (root-readable fields only)."""
from __future__ import annotations

from pathlib import Path


def firmware_facts() -> dict:
    out: dict = {}
    for key, fname in (("sys_vendor", "sys_vendor"), ("product_name", "product_name"),
                       ("bios_version", "bios_version"), ("bios_vendor", "bios_vendor")):
        p = Path("/sys/class/dmi/id") / fname
        try:
            out[key] = p.read_text().strip() or None
        except (OSError, PermissionError):
            out[key] = None
    return out
