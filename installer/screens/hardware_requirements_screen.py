"""Honest requirement checks."""
from __future__ import annotations


def check() -> dict:
    from pathlib import Path
    mem_mb = 0
    try:
        with open("/proc/meminfo") as fh:
            for line in fh:
                if line.startswith("MemTotal:"):
                    mem_mb = int(line.split()[1]) // 1024
    except OSError:
        pass
    import shutil
    return {"arch": "x86_64" if __import__("platform").machine() == "x86_64" else __import__("platform").machine(),
            "ram_ok": mem_mb >= 1900, "ram_mb": mem_mb,
            "uefi": Path("/sys/firmware/efi").exists()}
