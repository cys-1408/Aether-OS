"""aether-mount-manager — mounts, ejects, trash passthrough, disk health."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "libraries/libaether-core/python"))

from service_main import SystemService  # noqa: E402
import mount_service, partition_discovery, safe_eject, mount_events  # noqa: E402
from removable_mount_policy import policy_for  # noqa: E402
from ..disk_health.disk_health import smart_health  # noqa: E402


def build_service() -> SystemService:
    return SystemService("mount-manager", "storage", {
        "Storage.list": lambda p: partition_discovery.discover(),
        "Storage.mount": lambda p: _mount_logged(str(p.get("device", ""))),
        "Storage.unmount": lambda p: _unmount_logged(str(p.get("device", ""))),
        "Storage.eject": lambda p: safe_eject.eject(str(p.get("device", ""))),
        "Storage.policy": lambda p: policy_for(str(p.get("device", "")), bool(p.get("removable", False))),
        "Storage.disk_health": lambda p: smart_health(str(p.get("disk", ""))),
    })


def _mount_logged(device: str) -> dict:
    result = mount_service.mount(device)
    mount_events.record("mount", device, result.get("mountpoint"),
                        ok=result.get("ok"), error=result.get("error"))
    return result


def _unmount_logged(device: str) -> dict:
    result = mount_service.unmount(device)
    mount_events.record("unmount", device, ok=result.get("ok"), error=result.get("error"))
    return result


if __name__ == "__main__":
    build_service().run()
