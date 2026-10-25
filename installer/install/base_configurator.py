"""BaseConfigurator: hostname, timezone, locale, machine-id for the target."""
from __future__ import annotations

from pathlib import Path

from installer._process import run_argv
from installer.logging.installer_log import InstallerLog


class BaseConfigurator:
    def __init__(self, dry_run: bool = False, log: InstallerLog | None = None):
        self.dry_run = dry_run
        self.log = log or InstallerLog(echo=False)

    def configure(self, root: str, *, timezone: str = "UTC",
                  locale: str = "en_US.UTF-8",
                  keyboard_layout: str = "us",
                  privacy_choices: dict | None = None) -> dict:
        chroot = ["arch-chroot", root]
        etc = Path(root) / "etc"

        (etc / "hostname").write_text("aether\n")
        (etc / "vconsole.conf").write_text(
            f"KEYMAP={keyboard_layout}\nFONT=\n")
        (etc / "locale.conf").write_text(
            f"LANG={locale}\nLC_TIME={locale}\n")

        zoneinfo = Path(root) / f"usr/share/zoneinfo/{timezone}"
        if zoneinfo.exists():
            res = run_argv([*chroot, "ln", "-sf",
                            f"/usr/share/zoneinfo/{timezone}", "/etc/localtime"],
                           log=self.log, step="base-config", dry_run=self.dry_run)
            if not res.ok and not self.dry_run:
                self.log.step("base-config", f"timezone link failed: {res.stderr[-200:]}")
        else:
            self.log.step("base-config", f"timezone {timezone} not present; leaving UTC")

        run_argv([*chroot, "systemd-machine-id-setup"],
                 log=self.log, step="base-config", dry_run=self.dry_run)
        res = run_argv([*chroot, "locale-gen"],
                       log=self.log, step="base-config", dry_run=self.dry_run)
        if not res.ok and not self.dry_run:
            self.log.step("base-config", f"locale-gen rc={res.rc} (locale may lack a generator entry)")

        # Privacy defaults land in the target's aether config.
        if privacy_choices:
            self._apply_privacy(root, privacy_choices)
        return {"hostname": "aether", "timezone": timezone, "locale": locale}

    def _apply_privacy(self, root: str, choices: dict) -> None:
        from installer.logging.installer_log import InstallerLog  # noqa: F401
        cfg = Path(root) / "etc/aether/privacy-defaults.yaml"
        if not cfg.exists():
            src = Path(__file__).resolve().parents[2] / "rootfs/etc/aether/privacy-defaults.yaml"
            if src.exists():
                cfg.parent.mkdir(parents=True, exist_ok=True)
                cfg.write_text(src.read_text())
        user_cfg = Path(root) / "var/lib/aether/firstboot-privacy.json"
        user_cfg.parent.mkdir(parents=True, exist_ok=True)
        import json
        user_cfg.write_text(json.dumps(choices, indent=2))
