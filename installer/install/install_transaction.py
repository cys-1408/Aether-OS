"""The install transaction: orchestrates every installation step with a
journal, progress callbacks and automatic rollback on failure.

Steps (in order):
  backup-table -> partition -> format -> encrypt? -> mount -> fstab ->
  install-packages -> install-kernel -> initramfs -> bootloader ->
  base-config -> users -> desktop -> firstboot
"""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Callable

from ..app.installer_controller import InstallerController
from ..app.installer_error import E_ABORTED, InstallerError
from .._process import run_argv
from ..logging.installer_log import InstallerLog
from ..recovery.install_rollback import InstallRollback, backup_partition_table
from ..storage.encryption_setup import EncryptionSetup
from ..storage.filesystem_creator import FilesystemCreator
from ..storage.fstab_writer import build_crypttab, build_fstab, write_target_files
from ..storage.mount_plan import MountPlan
from ..storage.partition_planner import plan_partitions_to_sfdisk_script
from .base_configurator import BaseConfigurator
from .bootloader_installer import BootloaderInstaller
from .desktop_configurator import DesktopConfigurator
from .firstboot_configurator import leave_firstboot_pending
from .initramfs_installer import InitramfsInstaller
from .kernel_installer import KernelInstaller
from .package_installer import PackageInstaller, find_local_repo_dir
from .user_creator import UserCreator

JOURNAL_PATH = Path("/run/aether/installer-transaction.journal.jsonl")

ProgressCb = Callable[[dict], None]


class InstallTransaction:
    def __init__(self, controller: InstallerController, *,
                 log: InstallerLog | None = None,
                 progress_cb: ProgressCb | None = None):
        self.ctl = controller
        self.log = log or InstallerLog(echo=False)
        self.progress_cb = progress_cb or (lambda event: None)
        self.journal_path = JOURNAL_PATH
        self.completed: list[dict] = []
        self.table_backup: Path | None = None
        self.luks_created = False
        self.root_device: str | None = None

    # ------------------------------------------------------------------ #
    def run(self) -> dict:
        dry = self.ctl.dry_run
        plan = self.ctl.get("partition_plan", {})
        disk = str(self.ctl.get("target_disk"))
        encrypted = bool(self.ctl.get("encryption_enabled"))
        passphrase = self.ctl.get("luks_passphrase") or ""
        if encrypted:
            from ..logging.secret_filter import register_secret
            register_secret(passphrase)

        def step(name, fn):
            self._emit({"event": "step_started", "step": name})
            self._journal({"event": "step_started", "step": name})
            started = time.monotonic()
            try:
                detail = fn()
                duration = round(time.monotonic() - started, 3)
                record = {"step": name, "status": "done", "duration_s": duration,
                          "detail": detail}
                self.completed.append(record)
                self._journal({"event": "step_finished", "step": name,
                               "duration_s": duration})
                self._emit({"event": "step_finished", "step": name,
                            "duration_s": duration, "detail": detail})
                return record
            except Exception as exc:
                duration = round(time.monotonic() - started, 3)
                self._journal({"event": "step_failed", "step": name,
                               "error": str(exc)})
                self._emit({"event": "step_failed", "step": name, "error": str(exc)})
                raise

        try:
            self.ctl.refresh_guard_disk_identity()
            self.ctl.assert_guard_for_plan("install-transaction")

            step("backup-table", lambda: self._backup_table(disk, dry))
            step("partition", lambda: self._partition(disk, plan, dry))
            step("format", lambda: self._format(disk, plan, dry))

            root_device = self._resolve_root_device(disk, plan, dry)
            self.root_device = root_device
            esp_device = self._resolve_esp_device(disk, plan, dry)
            if encrypted:
                def do_encrypt():
                    enc = EncryptionSetup(dry_run=dry, log=self.log)
                    enc.luks_format(root_device, passphrase)
                    enc.luks_open(root_device, passphrase)
                    self.luks_created = True
                    return {"mapper": "/dev/mapper/aether-root"}
                step("encrypt", do_encrypt)
                mapper = "/dev/mapper/aether-root"
            else:
                mapper = root_device

            mount = MountPlan(encrypted=encrypted, root_device=mapper,
                              esp_device=esp_device, dry_run=dry, log=self.log)
            step("mount", mount.apply)

            def do_fstab():
                luks_uuid = None
                if encrypted:
                    luks_uuid = EncryptionSetup(dry_run=dry, log=self.log).luks_uuid(
                        root_device)
                fstab = build_fstab(root_device=mapper, esp_device=esp_device,
                                    encrypted=encrypted, dry_run=dry)
                crypttab = build_crypttab(luks_uuid) if encrypted else None
                if not dry:
                    write_target_files(fstab["fstab"], crypttab)
                return {"root_uuid": fstab["root_uuid"]}
            step("fstab", do_fstab)

            step("install-packages",
                 lambda: PackageInstaller(dry_run=dry, log=self.log).install_base())
            step("install-kernel",
                 lambda: KernelInstaller(dry_run=dry, log=self.log).ensure_kernel(
                     online=bool(self.ctl.get("network_mode") == "online"),
                     local_repo_dir=find_local_repo_dir()))
            step("initramfs",
                 lambda: InitramfsInstaller(dry_run=dry, log=self.log).install(
                     encrypted=encrypted,
                     locale=str(self.ctl.get("locale", "en_US.UTF-8")),
                     keyboard_layout=str(self.ctl.get("keyboard_layout", "us"))))
            step("bootloader",
                 lambda: BootloaderInstaller(dry_run=dry, log=self.log).install(
                     firmware=str(plan.get("firmware", "uefi")),
                     disk_path=disk, encrypted=encrypted))
            step("base-config",
                 lambda: BaseConfigurator(dry_run=dry, log=self.log).configure(
                     timezone=str(self.ctl.get("timezone")),
                     locale=str(self.ctl.get("locale")),
                     keyboard_layout=str(self.ctl.get("keyboard_layout", "us")),
                     privacy_choices=self.ctl.get("privacy_choices", {})))
            step("users",
                 lambda: UserCreator(dry_run=dry, log=self.log).create_user(
                     str(self.ctl.get("username")),
                     str(self.ctl.get("full_name")),
                     str(self.ctl.get("user_password")),
                     in_wheel_group=bool(self.ctl.get("wheel_enabled", True))))
            step("desktop",
                 lambda: DesktopConfigurator(dry_run=dry, log=self.log).configure())
            step("firstboot",
                 lambda: leave_firstboot_pending(
                     username=str(self.ctl.get("username")),
                     locale=str(self.ctl.get("locale")),
                     timezone=str(self.ctl.get("timezone")),
                     dry_run=dry))

            self._journal({"event": "transaction_done"})
            self._emit({"event": "done", "steps": len(self.completed)})
            return {"status": "complete", "steps": self.completed}
        except Exception as exc:
            self._journal({"event": "transaction_failed", "error": str(exc)})
            self._emit({"event": "failed", "error": str(exc)})
            rollback = self._rollback(disk, encrypted, passphrase, dry)
            self._emit({"event": "rollback_finished", "report": rollback})
            return {
                "status": "failed",
                "error": str(exc),
                "completed": self.completed,
                "rollback": rollback,
            }

    # ------------------------------------------------------------------ #
    def _rollback(self, disk: str, encrypted: bool, passphrase: str,
                  dry: bool) -> dict:
        executor = InstallRollback(dry_run=dry, log=self.log)
        return executor.rollback(
            disk_path=disk,
            table_backup=self.table_backup,
            luks_created=self.luks_created and encrypted,
            luks_partition=self.root_device if encrypted else None,
            luks_passphrase=passphrase if encrypted else None,
        )

    def _backup_table(self, disk: str, dry: bool) -> dict:
        self.table_backup = backup_partition_table(disk, dry_run=dry, log=self.log)
        return {"backup": str(self.table_backup)}

    def _partition(self, disk: str, plan: dict, dry: bool) -> dict:
        script = plan_partitions_to_sfdisk_script(plan)
        res = run_argv(["sfdisk", "--force", disk], log=self.log, step="partition",
                       dry_run=dry, input_bytes=script.encode("utf-8"))
        if not res.ok and not dry:
            raise RuntimeError(f"sfdisk failed: {res.stderr[-1500:]}")
        if not dry:
            # Ask the kernel to re-read the table before any mkfs touches it.
            run_argv(["partprobe", disk], log=self.log, step="partition")
        return {"sfdisk_script": script}

    def _format(self, disk: str, plan: dict, dry: bool) -> dict:
        creator = FilesystemCreator(dry_run=dry, log=self.log)
        esp_part = creator.resolve_root_partition(disk, role="esp")
        root_part = creator.resolve_root_partition(disk, role="root")
        if dry or not esp_part or not root_part:
            return {"partitions": [], "dry_run": True,
                    "note": "partition discovery skipped (dry-run or no partitions)"}
        outcomes = [creator.wipe_signatures(p) for p in (esp_part, root_part)]
        outcomes.append(creator.format_esp(esp_part))
        if not plan.get("encrypted"):
            outcomes.append(creator.format_root(root_part))
        return {"partitions": outcomes}

    def _resolve_root_device(self, disk: str, plan: dict, dry: bool) -> str:
        if dry:
            return disk + "2"
        creator = FilesystemCreator(dry_run=False, log=self.log)
        part = creator.resolve_root_partition(disk, role="root")
        if not part:
            raise InstallerError(E_ABORTED, "root partition not found after partitioning")
        return part

    def _resolve_esp_device(self, disk: str, plan: dict, dry: bool) -> str | None:
        if dry:
            return disk + "1"
        creator = FilesystemCreator(dry_run=False, log=self.log)
        return creator.resolve_root_partition(disk, role="esp")

    # ------------------------------------------------------------------ #
    def _journal(self, entry: dict) -> None:
        entry = {"ts": time.strftime("%Y-%m-%dT%H:%M:%S%z"), **entry}
        try:
            self.journal_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.journal_path, "a", encoding="utf-8") as fh:
                fh.write(json.dumps(entry, sort_keys=True, default=str) + "\n")
        except OSError:
            pass

    def _emit(self, event: dict) -> None:
        try:
            self.progress_cb(event)
        except Exception:
            pass
