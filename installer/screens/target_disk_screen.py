"""Target disk: EXACT device named, listed from real lsblk."""
from __future__ import annotations

import json
import subprocess


def disks() -> list[dict]:
    try:
        out = subprocess.run(["lsblk", "-J", "-d", "-o", "NAME,SIZE,MODEL,TYPE"],
                             capture_output=True, text=True, timeout=10)
        data = json.loads(out.stdout)
        return [d for d in data.get("blockdevices", []) if d.get("type") == "disk"]
    except (FileNotFoundError, subprocess.TimeoutExpired, json.JSONDecodeError):
        return []


def pick_disk_cli() -> str:
    ds = disks()
    if not ds:
        raise SystemExit("no disks detected (lsblk unavailable?)")
    for i, d in enumerate(ds, 1):
        print(f"  {i}. /dev/{d['name']}  {d.get('size', '?')}  {d.get('model', '')}")
    choice = input("Target disk number: ").strip()
    d = ds[int(choice) - 1]
    print(f"WARNING: ALL DATA on /dev/{d['name']} will be ERASED.")
    return f"/dev/{d['name']}"
