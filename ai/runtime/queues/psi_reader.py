"""PSI reader: /proc/pressure parsing (memory, cpu, io) — measured, truthful."""
from __future__ import annotations

from pathlib import Path

PROC_PRESSURE = Path("/proc/pressure")


def _parse_file(path: Path) -> dict:
    out: dict = {}
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return out
    for line in text.splitlines():
        if not line.strip():
            continue
        kind, _, rest = line.partition(" ")
        fields: dict[str, float] = {}
        for item in rest.split():
            if "=" in item:
                key, val = item.split("=", 1)
                try:
                    fields[key] = float(val)
                except ValueError:
                    pass
        out[kind] = fields
    return out


def pressure(kind: str = "memory") -> dict:
    """Return {avg10, avg60, avg300, supported} for a PSI resource."""
    data = _parse_file(PROC_PRESSURE / kind)
    if not data:
        return {"supported": False, "avg10": 0.0, "avg60": 0.0, "avg300": 0.0,
                "reason": f"/proc/pressure/{kind} unavailable (PSI disabled?)"}
    full = data.get("full", {})
    some = data.get("some", {})
    return {
        "supported": True,
        "avg10": full.get("avg10", some.get("avg10", 0.0)),
        "avg60": full.get("avg60", some.get("avg60", 0.0)),
        "avg300": full.get("avg300", some.get("avg300", 0.0)),
    }


def memory_avg10() -> float:
    return float(pressure("memory").get("avg10", 0.0))


def io_avg10() -> float:
    return float(pressure("io").get("avg10", 0.0))
