import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "libraries/libaether-core/python"))
"""aether-printing — CUPS facade."""
from service_main import SystemService  # noqa: E402
import print_service, queue_manager, scan_service, device_discovery  # noqa: E402


def build_service() -> SystemService:
    return SystemService("printing", "printing", {
        "Print.status": lambda p: print_service.status(),
        "Print.queue": lambda p: queue_manager.queue(p.get("printer")),
        "Print.print": lambda p: print_service.print_file(
            str(p.get("path", "")), p.get("printer"), int(p.get("copies", 1))),
        "Print.cancel": lambda p: queue_manager.cancel(str(p.get("job_id", ""))),
        "Print.scan_devices": lambda p: scan_service.devices(),
        "Print.scan": lambda p: scan_service.scan_to(str(p.get("path", "/tmp/aether-scan.png")), p.get("device")),
        "Print.devices": lambda p: device_discovery.discover(),
    })


if __name__ == "__main__":
    build_service().run()
