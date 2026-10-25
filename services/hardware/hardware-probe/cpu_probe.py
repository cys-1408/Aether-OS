"""Real CPU facts from /proc/cpuinfo + sysfs topology."""
from __future__ import annotations

import os
from pathlib import Path


def cpu_facts() -> dict:
    model, flags = None, []
    cores = threads = None
    arch = "x86_64" if os.uname().machine == "x86_64" else os.uname().machine
    try:
        for line in Path("/proc/cpuinfo").read_text().splitlines():
            if line.startswith("model name") and model is None:
                model = line.split(":", 1)[1].strip()
            if line.startswith("flags") and not flags:
                flags = line.split(":", 1)[1].split()
    except OSError:
        pass
    base = Path("/sys/devices/system/cpu")
    try:
        cpu_list = [p.name for p in base.glob("cpu[0-9]*")]
        threads = len(cpu_list) or None
        # physical cores = unique (core_id, physical_package_id) pairs
        pairs = set()
        for c in cpu_list:
            topo = base / c / "topology"
            try:
                core = (topo / "core_id").read_text().strip()
                pkg = (topo / "physical_package_id").read_text().strip()
                pairs.add((pkg, core))
            except OSError:
                continue
        cores = len(pairs) or threads
    except OSError:
        pass
    return {
        "model": model, "arch": arch, "cores": cores, "threads": threads,
        "flags": flags,
        "instruction_sets": [f for f in flags if f in ("sse4_2", "avx", "avx2", "avx512f", "fma", "neon")],
    }
