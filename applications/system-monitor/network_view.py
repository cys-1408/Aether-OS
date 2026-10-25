"""Network throughput from /proc/net/dev (real deltas)."""
from __future__ import annotations

import time


def interfaces() -> dict:
    out = {}
    try:
        for line in open("/proc/net/dev").read().splitlines()[2:]:
            name, data = line.split(":", 1)
            fields = data.split()
            out[name.strip()] = {"rx_bytes": int(fields[0]), "tx_bytes": int(fields[8])}
    except (OSError, ValueError, IndexError):
        pass
    return out


def throughput(sample_s: float = 1.0) -> dict:
    a = interfaces(); t0 = time.monotonic()
    time.sleep(sample_s)
    b = interfaces(); dt = time.monotonic() - t0
    return {name: {"rx_kbps": round((b[name]["rx_bytes"] - a[name]["rx_bytes"]) / dt / 1024, 1),
                   "tx_kbps": round((b[name]["tx_bytes"] - a[name]["tx_bytes"]) / dt / 1024, 1)}
            for name in b if name in a}
