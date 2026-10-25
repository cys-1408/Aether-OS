"""Device node permission queries from udev/sysfs."""
from __future__ import annotations

import os
import stat
from pathlib import Path


def device_permissions(dev_path: str) -> dict:
    p = Path(dev_path)
    if not p.exists():
        return {"exists": False, "dev_path": dev_path}
    st = os.stat(p)
    return {
        "exists": True,
        "dev_path": dev_path,
        "mode": oct(stat.S_IMODE(st.st_mode)),
        "owner_uid": st.st_uid,
        "group_gid": st.st_gid,
        "readable": os.access(p, os.R_OK),
        "writable": os.access(p, os.W_OK),
    }
