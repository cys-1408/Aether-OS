"""Machine profile: measured facts + labeled estimates."""
from __future__ import annotations

from pathlib import Path

from aether_core.config import load_yaml


def _cpu() -> dict:
    model, flags = None, []
    try:
        for line in Path("/proc/cpuinfo").read_text().splitlines():
            if line.startswith("model name") and not model:
                model = line.split(":", 1)[1].strip()
            if line.startswith("flags") and not flags:
                flags = line.split(":", 1)[1].split()
    except OSError:
        pass
    return {"model": model, "flags": flags, "arch": "x86_64"}


def _memory() -> dict:
    total = avail = 0
    try:
        with open("/proc/meminfo") as fh:
            for line in fh:
                if line.startswith("MemTotal:"):
                    total = int(line.split()[1]) // 1024
                elif line.startswith("MemAvailable:"):
                    avail = int(line.split()[1]) // 1024
    except (OSError, ValueError):
        pass
    return {"total_mb": total, "available_mb": avail}


def _accelerators() -> list[dict]:
    out = []
    from pathlib import Path as P
    vendors = {0x8086: "Intel", 0x10DE: "NVIDIA", 0x1002: "AMD"}
    try:
        devices = list(P("/sys/bus/pci/devices").iterdir())
    except OSError:
        return out
    for pci in devices:
        try:
            cls = int((pci / "class").read_text().strip(), 16) >> 16
        except (OSError, ValueError):
            continue
        if (cls & 0xFF00) != 0x0300:
            continue
        vendor = None
        try:
            vendor = vendors.get(int((pci / "vendor").read_text().strip(), 16))
        except (OSError, ValueError):
            pass
        vram = None
        mf = pci / "mem_info_vram_total"
        if mf.exists():
            try:
                vram = int(mf.read_text().strip()) // (1024 * 1024)
            except (OSError, ValueError):
                pass
        driver = (pci / "driver").resolve().name if (pci / "driver").exists() else None
        out.append({"type": "gpu", "vendor": vendor, "driver": driver, "vram_mb": vram,
                    "unsupported_reason": None if driver else "no driver bound"})
    return out


def profile_machine(config: dict) -> dict:
    mem = _memory()
    reserves = config.get("memory", {})
    os_reserve = int(reserves.get("os_reserve_mb", 1024))
    desktop_reserve = int(reserves.get("desktop_reserve_mb", 1024))
    budget = max(0, mem["available_mb"] - os_reserve - desktop_reserve)
    return {
        "schema_version": "1.0.0",
        "cpu": _cpu(),
        "memory": mem,
        "accelerators": _accelerators(),
        "estimates": {
            "inference_memory_budget_mb": budget,
            "note": "estimate = available_mb - os_reserve - desktop_reserve (labeled ESTIMATE)",
        },
        "power": _power(),
        "thermal": _thermal(),
        "unknown_fields": [k for k, v in (("accel_vram", _accelerators()),) if not v],
    }


def _power() -> dict:
    ac = None
    for ps in Path("/sys/class/power_supply").glob("*"):
        try:
            if (ps / "type").read_text().strip() == "Mains":
                ac = (ps / "online").read_text().strip() == "1"
        except OSError:
            continue
    return {"ac_online": ac}


def _thermal() -> list[dict]:
    zones = []
    for z in Path("/sys/class/thermal").glob("thermal_zone*"):
        try:
            zones.append({"zone": z.name, "temp_c": int((z / "temp").read_text().strip()) / 1000})
        except (OSError, ValueError):
            continue
    return zones
