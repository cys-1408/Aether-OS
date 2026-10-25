"""NPU probe: class 0x12 PCI devices (honest absence)."""
from __future__ import annotations

from pathlib import Path


def npus() -> list[dict]:
    out = []
    try:
        devices = list(Path("/sys/bus/pci/devices").iterdir())
    except OSError:
        return out
    for pci in devices:
        try:
            cls = int((pci / "class").read_text().strip(), 16) >> 16
        except (OSError, ValueError):
            continue
        if (cls & 0xFF00) == 0x1200:
            out.append({"type": "npu", "pci_addr": pci.name})
    return out
