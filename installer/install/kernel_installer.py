"""KernelInstaller: stage the Aether kernel + modules into the target root.

Prefers the pre-built artifact from the local repository (linux-aether
package); falls back to an online `pacman -S linux-aether` when network
installation was explicitly chosen.
"""
from __future__ import annotations

import json
import subprocess
from pathlib import Path

from installer._process import run_argv
from installer.logging.installer_log import InstallerLog


class KernelInstaller:
    def __init__(self, dry_run: bool = False, log: InstallerLog | None = None):
        self.dry_run = dry_run
        self.log = log or InstallerLog(echo=False)

    def ensure_kernel(self, root: str, online: bool = False,
                      local_repo_dir: Path | None = None) -> dict:
        boot = Path(root) / "boot"
        vmlinuz = boot / "vmlinuz-aether"
        if vmlinuz.exists():
            return {"kernel": str(vmlinuz), "present": True, "source": "already-installed"}

        # 1) kernel package from the local repo
        if local_repo_dir is not None:
            res = run_argv(["pacman", "-r", root, "-S", "--noconfirm", "--config",
                            str(local_repo_dir / "repo.conf" if (local_repo_dir / "repo.conf").exists()
                                else "/run/aether/pacman-local.conf"),
                            "linux-aether", "linux-aether-modules"],
                           log=self.log, step="install-kernel", dry_run=self.dry_run)
            if res.ok or self.dry_run:
                if vmlinuz.exists() or self.dry_run:
                    return {"kernel": str(vmlinuz), "present": True, "source": "local-repo"}

        # 2) explicit online path
        if online:
            chroot = ["arch-chroot", root] if not self.dry_run else []
            res = run_argv([*chroot, "pacman", "-S", "--noconfirm", "linux-aether"],
                           log=self.log, step="install-kernel", dry_run=self.dry_run)
            if res.ok and vmlinuz.exists() or self.dry_run:
                return {"kernel": str(vmlinuz), "present": True, "source": "online"}

        raise RuntimeError(
            "kernel is not installed in the target and no local repository was "
            "available; refusing to continue without a kernel")

    def record_provenance(self, root: str, out: Path) -> dict:
        """Write the kernel provenance snippet for the install report."""
        prov = {}
        commit_file = Path("/run/aether/kernel-provenance.json")
        if commit_file.exists():
            try:
                prov = json.loads(commit_file.read_text())
            except json.JSONDecodeError:
                prov = {}
        try:
            tgt = Path(root) / "etc/aether/kernel-provenance.json"
            tgt.parent.mkdir(parents=True, exist_ok=True)
            tgt.write_text(json.dumps(prov, indent=2))
        except OSError:
            pass
        return prov
