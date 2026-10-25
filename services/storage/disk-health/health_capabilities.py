"""What this host can report about disk health."""
from __future__ import annotations

import shutil


def capabilities() -> dict:
    return {
        "smart": shutil.which("smartctl") is not None,
        "nvme_cli": shutil.which("nvme") is not None,
        "btrfs_scrub_status": shutil.which("btrfs") is not None,
    }
