"""Post-update health checks; failures trigger the rollback policy."""
from __future__ import annotations

import subprocess
import time

HEALTH_CHECKS = [
    ("boot_entry", ["systemctl", "--root=/", "get-default"]),
    ("service_manager", ["pidof", "systemd"]),
    ("network_manager", ["systemctl", "is-active", "NetworkManager.service"]),
    ("aether_services", ["systemctl", "is-system-running"]),
]

ROLLOVER_FAILURES = ["boot_entry", "aether_services"]


def run_health_check() -> dict:
    results = []
    passed, failed = [], []
    for name, argv in HEALTH_CHECKS:
        try:
            out = subprocess.run(argv, capture_output=True, text=True, timeout=30)
            ok = out.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired) as exc:
            out = None
            ok = False
            detail = str(exc)
        results.append({"check": name, "ok": ok})
        (passed if ok else failed).append(name)

    report = {
        "checked_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "healthy": not any(f in ROLLOVER_FAILURES for f in failed),
        "checks_passed": passed,
        "checks_failed": failed,
        "detail": results,
    }
    report["rollback_required"] = not report["healthy"]
    return report
