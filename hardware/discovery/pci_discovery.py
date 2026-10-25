"""PCI device discovery (real sysfs walk)."""
from __future__ import annotations

from pathlib import Path

VENDORS = {0x8086: "Intel", 0x10DE: "NVIDIA", 0x1002: "AMD", 0x14C3: "MediaTek",
           0x168C: "Qualcomm Atheros", 0x10EC: "Realtek", 0x15AD: "VMware"}


def discover() -> list[dict]:
    out = []
    try:
        devices = list(Path("/sys/bus/pci/devices").iterdir())
    except OSError:
        return out
    for pci in devices:
        try:
            cls = int((pci / "class").read_text().strip(), 16) >> 16
            vendor = int((pci / "vendor").read_text().strip(), 16)
        except (OSError, ValueError):
            continue
        driver = (pci / "driver").resolve().name if (pci / "driver").exists() else None
        out.append({"pci_addr": pci.name, "class": hex(cls),
                    "vendor": VENDORS.get(vendor, hex(vendor)),
                    "driver": driver})
    return out
