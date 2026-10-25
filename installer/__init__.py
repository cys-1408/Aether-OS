"""AetherOS installer package.

Runs from the AetherOS live ISO as root. Drives parted/sfdisk/mkfs/cryptsetup/
pacstrap/grub-install through strict argv subprocess calls. Every destructive
operation is gated by installer.storage.destructive_action_guard.
"""

__all__ = ["app", "storage", "install", "logging", "recovery", "schemas"]
__version__ = "1.0.0"
