"""DesktopConfigurator: enable Aether units + greetd in the target."""
from __future__ import annotations

from pathlib import Path

from installer._process import run_argv
from installer.logging.installer_log import InstallerLog

UNIT_GROUPS = [
    "NetworkManager.service", "aether-hardware-probe.service",
    "aether-health.service", "aether-notification.service",
    "aether-intentfs.service", "aether-ledger.service",
    "aether-workspace.service", "aether-update-check.timer",
    "aether-runtime.service", "aether-agent.service",
    "aether-broker.service", "aether-recovery.service",
    "greetd.service",
]


class DesktopConfigurator:
    def __init__(self, dry_run: bool = False, log: InstallerLog | None = None):
        self.dry_run = dry_run
        self.log = log or InstallerLog(echo=False)

    def configure(self, root: str) -> dict:
        chroot = ["arch-chroot", root]
        enabled: list[str] = []
        for unit in UNIT_GROUPS:
            res = run_argv([*chroot, "systemctl", "enable", unit],
                           log=self.log, step="desktop", dry_run=self.dry_run)
            if res.ok or self.dry_run:
                enabled.append(unit)
            else:
                self.log.step("desktop", f"enable failed for {unit}: {res.stderr[-200:]}")
        run_argv([*chroot, "systemctl", "set-default", "aether-graphical.target"],
                 log=self.log, step="desktop", dry_run=self.dry_run)
        return {"enabled": enabled}

    # Back-compat flat entry point.
    def enable(self, root: str) -> dict:
        return self.configure(root)
