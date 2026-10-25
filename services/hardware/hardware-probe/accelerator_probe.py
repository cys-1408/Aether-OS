"""GPU/NPU discovery via /sys/bus/pci — never assumes one exists."""
from __future__ import annotations

from pathlib import Path

VENDORS = {0x8086: "Intel", 0x10DE: "NVIDIA", 0x1002: "AMD", 0x15AD: "VMware", 0x1234: "Bochs"}


def _driver_of(pci: Path) -> str | None:
    link = pci / "driver"
    return link.resolve().name if link.exists() else None


def accelerators() -> list[dict]:
    out = []
    base = Path("/sys/bus/pci/devices")
    try:
        devices = list(base.iterdir())
    except OSError:
        devices = []
    for pci in devices:
        try:
            class_id = (pci / "class").read_text().strip()
        except OSError:
            continue
        cls = int(class_id, 16) >> 16 if class_id else 0
        if (cls & 0xFF00) == 0x0300:
            kind = "gpu"
        elif (cls & 0xFF00) == 0x1200:
            kind = "npu"
        else:
            continue
        vendor_id = None
        try:
            vendor_id = int((pci / "vendor").read_text().strip(), 16)
        except (OSError, ValueError):
            pass
        vram_mb = None
        for mem_file in ("mem_info_vram_total", "mem_info_gtt_total"):
            mf = pci / mem_file
            if mf.exists():
                try:
                    vram_mb = int(mf.read_text().strip()) // (1024 * 1024)
                    break
                except (OSError, ValueError):
                    pass
        driver = _driver_of(pci)
        out.append({
            "type": kind,
            "vendor": VENDORS.get(vendor_id) if vendor_id else None,
            "model": None,  # sysfs lacks the marketing name; enriched via lspci when present
            "pci_addr": pci.name,
            "driver": driver,
            "vram_mb": vram_mb,
            "unsupported_reason": None if driver else "no kernel driver bound",
        })
    return out
