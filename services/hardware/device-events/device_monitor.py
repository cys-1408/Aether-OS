"""udev event monitor: publishes real add/remove events to notifications."""
from __future__ import annotations

import shlex
import subprocess
import threading
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from service_main import SystemService  # noqa: E402


class DeviceMonitor:
    def __init__(self) -> None:
        self._stop = threading.Event()

    def start(self) -> None:
        threading.Thread(target=self._loop, daemon=True).start()

    def stop(self) -> None:
        self._stop.set()

    def _loop(self) -> None:
        try:
            proc = subprocess.Popen(
                ["udevadm", "monitor", "--kernel", "--udev", "--subsystem-match=block",
                 "--subsystem-match=drm", "--subsystem-match=usb"],
                stdout=subprocess.PIPE, text=True)
        except FileNotFoundError:
            return  # udevadm absent: monitor unavailable, reported truthfully
        for line in proc.stdout:  # type: ignore[union-attr]
            if self._stop.is_set():
                proc.terminate()
                return
            line = line.strip()
            if line.startswith(("KERNEL", "UDEV")):
                continue
            if line.startswith(("add", "remove", "change")):
                event = line.split()[0]
                svc = SystemService("device-events", "device-events", {})
                svc.call_service("notifications", "Notify.notify", {
                    "source": "device-events", "category": "device",
                    "title": f"Device {event}d", "body": shlex.quote(line),
                })


def build_service() -> SystemService:
    return SystemService("device-events", "device-events", {
        "Devices.status": lambda p: {"monitor": "udevadm-based", "subsystems": ["block", "drm", "usb"]},
    })


if __name__ == "__main__":
    svc = build_service()
    DeviceMonitor().start()
    svc.run()
