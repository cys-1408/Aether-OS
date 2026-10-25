"""Detect installed Aether roots via blkid + fstab hints."""
from __future__ import annotations

import subprocess


def detect_installed() -> str | None:
    try:
        out = subprocess.run(["blkid"], capture_output=True, text=True, timeout=15)
        for line in out.stdout.splitlines():
            if 'LABEL="AETHEROS"' in line or 'TYPE="ext4"' in line:
                dev = line.split(":")[0]
                mnt = "/mnt/recovery-target"
                subprocess.run(["mkdir", "-p", mnt], check=False)
                if subprocess.run(["mount", dev, mnt], capture_output=True, timeout=30).returncode == 0:
                    if (subprocess.run(["test", "-d", mnt + "/etc/aether"]).returncode == 0):
                        return mnt
                    subprocess.run(["umount", mnt], timeout=30)
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass
    return None
