"""USB discovery (lsusb when present, sysfs fallback)."""
from __future__ import annotations

import subprocess
from pathlib import Path


def discover() -> list[dict]:
    try:
        out = subprocess.run(["lsusb"], capture_output=True, text=True, timeout=10)
        return [{"line": l.strip()} for l in out.stdout.splitlines() if l.strip()]
    except FileNotFoundError:
        out = []
        try:
            for dev in Path("/sys/bus/usb/devices").iterdir():
                if ":" not in dev.name:
                    prod = dev / "product"
                    out.append({"id": dev.name,
                                "product": prod.read_text().strip() if prod.exists() else None})
        except OSError:
            pass
        return out
