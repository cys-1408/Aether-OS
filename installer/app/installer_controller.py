"""Install orchestration: state journal + destructive guard + step modules.

Two entry points live here:
- run_plan(plan): flat step flow used by the GTK screens and CLI.
- install_transaction(): routed through install/install_transaction.py, which
  journals every step and rolls back. Both use the same class modules; the
  monotonic controller API (get/, arm guard, refresh) satisfies the
  transaction's expectations.
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
for sub in ("storage", "install", "logging", HERE.parents[0]):
    p = HERE.parent / sub if sub != HERE.parents[0] else HERE.parents[0]
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))
HERE = Path(__file__).resolve().parent
# Shared 'aether_core' (CONVENTIONS.md §3)
_LIBAETHER = HERE.parents[2] / "libraries" / "libaether-core" / "python"
if _LIBAETHER.is_dir() and str(_LIBAETHER) not in sys.path:
    sys.path.insert(0, str(_LIBAETHER))

from installer_state import InstallerState  # noqa: E402
from installer_error import InstallerError  # noqa: E402
import installer_log  # noqa: E402

STEPS = ["precheck", "partition", "encrypt", "format", "mount", "pacstrap",
         "kernel", "initramfs", "bootloader", "base_config", "user",
         "desktop", "firstboot"]

SUPPORTED_FIRMWARE = ("uefi", "bios")


class InstallerController:
    def __init__(self, state: InstallerState | None = None, dry_run: bool = False):
        self.state = state or InstallerState()
        self.dry_run = dry_run
        self.log = installer_log.InstallerLog()
        self._guard = None

    # ------------------------------------------------------- controller API
    def attach_guard(self, guard) -> None:
        self._guard = guard

    def refresh_guard_disk_identity(self) -> dict:
        if self._guard is None:
            from storage.destructive_action_guard import DestructiveActionGuard  # noqa: F401
            self._guard = DestructiveActionGuard()
        disk = str(self.get("target_disk") or "")
        if disk and not self._guard.disk:
            self._guard.arm(disk)
        return self._guard.refresh() if hasattr(self._guard, "refresh") else {}

    def assert_guard_for_plan(self, stage: str) -> None:
        target = str(self.get("target_disk") or "")
        # Which disk the guard was armed for?
        if str(self.get("guard_disk") or "") and self._guard is not None \
                and self._guard.disk and self._guard.disk != target:
            raise InstallerError(stage,
                                 f"guard disk {self._guard.disk} != target {target}")
        result = (self._guard.verify() if self._guard is not None
                  and hasattr(self._guard, "verify") else {"ok": True})
        if not result.get("ok", True):
            raise InstallerError(stage, result.get("reason", "guard verify failed"))

    def get(self, key: str, default=None):
        """Choice reads from the persisted state + runtime kwargs."""
        env = getattr(self, "_kwargs", {}) or {}
        if key in env:
            return env[key]
        return self.state.data.get(key, self.state.choices_merged().get(key, default))

    def set(self, key: str, value) -> None:
        self.state.data[key] = value

    # ----------------------------------------------------------- plan-flow
    def run_plan(self, plan: dict, progress=None) -> dict:
        """plan: target_disk, encryption{enabled,passphrase}, user{...}, choices."""
        self._kwargs = dict(plan)
        disk = plan["target_disk"]
        encrypted = bool(plan.get("encryption", {}).get("enabled"))
        if self._guard is None:
            from storage.destructive_action_guard import DestructiveActionGuard
            self._guard = DestructiveActionGuard()
        self._guard.arm(disk)
        self.set("target_disk", disk)
        self.set("encryption_enabled", encrypted)
        self.set("luks_passphrase", plan.get("encryption", {}).get("passphrase", ""))
        user = plan.get("user", {})
        if user:
            self.set("username", user.get("username", ""))
            self.set("user_password", user.get("password", ""))

        if not self.dry_run:
            from storage.destructive_action_guard import require_confirmation, backup_partition_table as backup_table
            require_confirmation(disk, plan.get("confirm_typed", ""))
            self._guard.typed_confirmation(plan.get("confirm_typed", ""))
            backup_table(disk)
        self.log.step("precheck", f"target={disk}")
        self.state.commit("precheck", {"target_disk": disk})

        try:
            self.state.commit("precheck")  # idempotent
            from storage.partition_planner import write_plan
            from storage.filesystem_creator import FilesystemCreator
            from storage.encryption_setup import EncryptionSetup
            from storage.mount_plan import MountPlan
            from install.package_installer import PackageInstaller
            from install.kernel_installer import KernelInstaller
            from install.initramfs_installer import InitramfsInstaller
            from install.bootloader_installer import BootloaderInstaller
            from install.base_configurator import BaseConfigurator
            from install.user_creator import UserCreator
            from install.desktop_configurator import DesktopConfigurator
            from install.firstboot_configurator import prepare, leave_firstboot_pending

            part_writer = write_plan(disk, dry_run=self.dry_run,
                                     plan={"firmware": "uefi", "encrypted": encrypted})
            self.state.commit("partition")

            if encrypted:
                EncryptionSetup(dry_run=self.dry_run).format_and_open(
                    disk, plan["encryption"]["passphrase"], dry_run=self.dry_run)
                self.state.commit("encrypt")

            fs = FilesystemCreator(dry_run=self.dry_run)
            fs.make_filesystems(disk)
            self.state.commit("format")

            mounts = MountPlan(encrypted=encrypted,
                               root_device=(f"{disk}2"), esp_device=(f"{disk}1"),
                               dry_run=self.dry_run).apply()
            self.state.commit("mount")

            PackageInstaller(dry_run=self.dry_run).install_base(mounts["root"])
            self.state.commit("pacstrap")
            KernelInstaller(dry_run=self.dry_run).ensure_kernel(
                mounts["root"], online=True)
            InitramfsInstaller(dry_run=self.dry_run).rebuild(
                mounts["root"], encrypted=encrypted)
            BootloaderInstaller(dry_run=self.dry_run).install(
                root=mounts["root"], firmware="uefi", disk_path=disk,
                encrypted=encrypted)
            for s in ("kernel", "initramfs", "bootloader"):
                self.state.commit(s)

            BaseConfigurator(dry_run=self.dry_run).configure(
                root=mounts["root"], timezone=plan.get("choices", {}).get("timezone", "UTC"))
            if plan.get("user"):
                UserCreator(dry_run=self.dry_run).create_user(
                    mounts["root"], user["username"], user.get("full_name", ""),
                    user.get("password", ""))
            self.state.commit("user")
            DesktopConfigurator(dry_run=self.dry_run).configure(mounts["root"])
            leave_firstboot_pending(mounts["root"], username=user.get("username"))
            self.state.commit("desktop")
            self.state.commit("firstboot")
            self.log.step("complete", "installation finished")
            return {"ok": True, "root": mounts["root"]}
        except InstallerError:
            raise
        except Exception as e:  # noqa: BLE001 — real failure path with rollback
            self.log.step("failed", str(e))
            _recovery_here = HERE.parents[1] / "recovery"
            if str(_recovery_here) not in sys.path:
                sys.path.insert(0, str(_recovery_here))
            from install_rollback import InstallRollback
            rollback = InstallRollback(dry_run=self.dry_run).rollback(
                disk_path=disk, table_backup=None, luks_created=encrypted,
                luks_partition=f"{disk}2" if encrypted else None,
                luks_passphrase=(plan.get("encryption", {}).get("passphrase", "")
                                 if encrypted else None))
            last = (self.state.data["completed_steps"][-1]
                    if self.state.data["completed_steps"] else "install")
            raise InstallerError(last, str(e))
