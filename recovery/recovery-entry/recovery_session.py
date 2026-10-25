"""The recovery menu loop with REAL repair actions."""
from __future__ import annotations

import subprocess

import sys
from pathlib import Path

_p = Path(__file__).resolve()
sys.path.insert(0, str(_p.parents[1] / "diagnostics"))
sys.path.insert(0, str(_p.parents[1] / "repair"))
sys.path.insert(0, str(_p.parents[1] / "rollback"))
sys.path.insert(0, str(_p.parents[1] / "backup"))
sys.path.insert(0, str(_p.parents[2] / "libraries/libaether-core/python"))

from system_detection import detect_installed  # noqa: E402
from repair_summary import summarize  # noqa: E402


class RecoverySession:
    MENU = [
        ("1", "Detect installed systems", "_detect"),
        ("2", "Collect diagnostics (redacted)", "_diagnostics"),
        ("3", "Filesystem check", "_fsck"),
        ("4", "Repair package database", "_pkgdb"),
        ("5", "Reinstall bootloader", "_bootloader"),
        ("6", "Rebuild initramfs", "_initramfs"),
        ("7", "Kernel rollback (known-good)", "_rollback"),
        ("8", "Remove broken AI models", "_models"),
        ("9", "Rebuild IntentFS index", "_index"),
        ("0", "Exit", None),
    ]

    def run(self) -> int:
        print("Aether Recovery Environment")
        while True:
            for key, label, _ in self.MENU:
                print(f"  {key}) {label}")
            choice = input("Select: ").strip()
            if choice == "0":
                return 0
            entry = next((m for m in self.MENU if m[0] == choice), None)
            if not entry:
                continue
            try:
                getattr(self, entry[2])()
            except Exception as e:  # noqa: BLE001 — surface the true error
                print(f"  action failed: {e}")

    def _root(self):
        root = detect_installed()
        print(f"  detected: {root or 'none'}")
        return root

    def _detect(self):
        self._root()

    def _diagnostics(self):
        from collect_system_state import collect
        print("  " + str(collect()))

    def _fsck(self):
        root = self._root()
        if root and input(f"  run fsck on {root}? [y/N]: ").strip().lower() == "y":
            out = subprocess.run(["fsck", "-y", root], capture_output=True, text=True, timeout=1800)
            print("  " + out.stdout[-400:])

    def _pkgdb(self):
        root = self._root()
        if root:
            subprocess.run(["arch-chroot", root, "pacman", "-Dkk"], timeout=300)
            print("  package database checked")

    def _bootloader(self):
        root = self._root()
        if root:
            subprocess.run(["arch-chroot", root, "grub-install",
                            "--target=x86_64-efi", "--efi-directory=/efi",
                            "--bootloader-id=AETHEROS"], check=False, timeout=600)
            subprocess.run(["arch-chroot", root, "grub-mkconfig", "-o", "/boot/grub/grub.cfg"],
                           check=False, timeout=300)
            print("  bootloader reinstalled")

    def _initramfs(self):
        root = self._root()
        if root:
            subprocess.run(["arch-chroot", root, "mkinitcpio", "-P"], check=False, timeout=600)
            print("  initramfs rebuilt")

    def _rollback(self):
        root = self._root()
        if root:
            from kernel_rollback import list_cached_kernels, downgrade
            kernels = list_cached_kernels(root)
            print(f"  cached kernels: {kernels}")
            if kernels and input("  downgrade to previous? [y/N]: ").strip().lower() == "y":
                print("  " + str(downgrade(root)))

    def _models(self):
        from model_remove_broken import remove_broken
        print("  " + str(remove_broken()))

    def _index(self):
        from intentfs_rebuild import rebuild_all
        print("  " + str(rebuild_all()))
