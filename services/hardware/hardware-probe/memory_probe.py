"""Real memory facts: meminfo, PSI, swap, zram."""
from __future__ import annotations

from pathlib import Path


def _parse_kb(line: str) -> int | None:
    try:
        return int(line.split(":")[1].strip().split()[0])
    except (IndexError, ValueError):
        return None


def memory_facts() -> dict:
    total = available = None
    try:
        for line in Path("/proc/meminfo").read_text().splitlines():
            if line.startswith("MemTotal:"):
                total = _parse_kb(line)
            elif line.startswith("MemAvailable:"):
                available = _parse_kb(line)
    except OSError:
        pass
    swap_total = None
    try:
        for line in Path("/proc/swaps").read_text().splitlines()[1:]:
            parts = line.split()
            if len(parts) >= 4 and parts[0] != "Filename":
                swap_total = (swap_total or 0) + int(parts[3]) // 1024
    except (OSError, ValueError):
        pass
    zram = None
    zram_path = Path("/sys/block/zram0/disksize")
    if zram_path.exists():
        try:
            zram = int(zram_path.read_text().strip()) // (1024 * 1024)
        except (OSError, ValueError):
            pass
    psi = None
    try:
        for line in Path("/proc/pressure/memory").read_text().splitlines():
            if line.startswith("some avg10="):
                psi = float(line.split("avg10=")[1].split()[0])
    except (OSError, ValueError):
        pass
    return {
        "total_mb": total // 1024 if total else None,
        "available_mb": available // 1024 if available else None,
        "swap_total_mb": swap_total, "zram_mb": zram, "psi_mem_avg10": psi,
    }
