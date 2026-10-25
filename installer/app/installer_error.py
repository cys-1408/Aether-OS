"""Installer errors with user-facing truth. Step codes are stable identifiers."""
from __future__ import annotations

# Stable step codes (used by the transaction journal and recovery screens).
E_PRECHECK = "precheck"
E_PARTITION = "partition"
E_FORMAT = "format"
E_ENCRYPT = "encrypt"
E_MOUNT = "mount"
E_PACKAGES = "install-packages"
E_KERNEL = "install-kernel"
E_INITRAMFS = "initramfs"
E_BOOTLOADER = "bootloader"
E_BASE_CONFIG = "base-config"
E_USERS = "users"
E_DESKTOP = "desktop"
E_FIRSTBOOT = "firstboot"
E_ABORTED = "aborted"


class InstallerError(Exception):
    def __init__(self, step: str, reason: str):
        super().__init__(f"{step}: {reason}")
        self.step = step
        self.reason = reason
