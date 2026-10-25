"""Capability get_cpu_memory_status — actual /proc measurements.

Reads are done directly on /proc/stat and /proc/meminfo; no hard-coded
values anywhere. Each field carries the raw observation so the UI can show
measured facts separately from any interpretation.
"""

from __future__ import annotations

import time


def _cpu_percentages() -> list[float]:
    """Per-core busy-fraction vs. the previous read (100ms delta window)."""
    def snapshot():
        lines = {}
        with open("/proc/stat") as fh:
            for line in fh:
                if line.startswith("cpu"):
                    parts = line.split()
                    lines[parts[0]] = [int(x) for x in parts[1:]]
        return lines

    first = snapshot()
    time.sleep(0.1)
    second = snapshot()
    out = []
    for name in sorted(second):
        if name not in first:
            continue
        deltas = [b - a for a, b in zip(first[name], second[name])]
        total = sum(deltas)
        idle = deltas[3] + (deltas[4] if len(deltas) > 4 else 0)
        out.append(round((total - idle) * 100.0 / total, 2) if total else 0.0)
    return out


def _memory() -> dict:
    info = {}
    with open("/proc/meminfo") as fh:
        for line in fh:
            key, _, val = line.partition(":")
            info[key.strip()] = int(val.strip().split()[0])  # kB
    total = info.get("MemTotal", 0)
    avail = info.get("MemAvailable", 0)
    return {
        "mem_total_kib": total,
        "mem_available_kib": avail,
        "mem_used_percent": round((total - avail) * 100.0 / total, 2) if total else None,
        "swap_total_kib": info.get("SwapTotal", 0),
        "swap_free_kib": info.get("SwapFree", 0),
        "psi_present": "PSI" in info or _psi_file_present(),
    }


def _psi_file_present() -> bool:
    from pathlib import Path
    return Path("/proc/pressure/memory").exists()


def execute(params: dict, ctx: dict | None = None) -> dict:
    try:
        cpu = _cpu_percentages()
    except OSError as e:
        return {"available": False, "reason": f"cpu read failed: {e}"}
    try:
        mem = _memory()
    except OSError as e:
        mem = {"available": False, "reason": f"meminfo read failed: {e}"}
    return {"available": True, "cpu": {"per_core_busy_percent": cpu, "cores": len(cpu)},
            "memory": mem, "measured_at": time.time()}


def run(params: dict, peer_uid: int | None = None) -> dict:
    return execute(params if isinstance(params, dict) else {},
                   ctx={"uid": peer_uid} if peer_uid is not None else None)
